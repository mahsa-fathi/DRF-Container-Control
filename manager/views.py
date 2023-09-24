from .models import Application, RunLog
from .serializers import AppSerializer, RunLogsSerializer
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from datetime import datetime
import docker


class ApplicationApiView(generics.RetrieveUpdateDestroyAPIView):
    """
    This class handle get, put, and delete requests on applications
    """
    serializer_class = AppSerializer
    queryset = Application.objects.all()

    def delete(self, request, *args, **kwargs):
        """
        delete removes all the containers of application and then calls super().delete
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        client = docker.from_env()
        containers = client.containers.list()
        instance = self.get_object()
        image_name = instance.image
        if ':' not in instance.image:
            image_name = instance.image + ":latest"

        for container in containers:
            if image_name in container.image.tags:
                try:
                    container.remove(force=True)
                except docker.errors.APIError as e:
                    # if containers could not be stopped an error will be returned
                    return Response(data={"details": f"Error removing container {container.name}: {e}"},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return super().delete(request, *args, **kwargs)


class ApplicationListApiView(generics.ListAPIView):
    """
    This class handles listing all applications in the database
    """
    queryset = Application.objects.all()
    serializer_class = AppSerializer

    def get(self, request, *args, **kwargs):
        """
        Overriding get function to add count of data to output
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        response = super().get(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            response_data = {
                'count': len(response.data),
                'results': response.data,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return response


class RunLogsListApiView(generics.ListAPIView):
    """
    This class handles listing the history of runs for a specific application id
    """
    queryset = RunLog.objects.all()
    serializer_class = RunLogsSerializer

    def get_queryset(self):
        """
        changing queryset by filtering on application id
        :return:
        """
        app_id = self.kwargs.get('id')
        queryset = RunLog.objects.filter(application_id=app_id)
        return queryset

    def get(self, request, *args, **kwargs):
        """
        Overriding get function to add count of data to output
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        response = super().get(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            response_data = {
                'count': len(response.data),
                'results': response.data,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return response


class BuildApplicationApiView(generics.CreateAPIView):
    # This class handles creation of a new application in database
    serializer_class = AppSerializer


@api_view(['GET'])
def run_app(request, pk):
    """
    This function handle run API for specific application
    :param request:
    :param pk:
    :return:
    """
    client = docker.from_env()

    details = Application.objects.filter(pk=pk).first()

    if details is None:
        # return 404 if application id was incorrect
        return Response({"details": "Application not found"}, status=status.HTTP_404_NOT_FOUND)

    image_name = details.image
    if ':' not in details.image:
        # adding latest tag to image
        image_name = details.image + ":latest"

    try:
        client.images.pull(repository=image_name)
    except docker.errors.APIError as e:
        # return 500 if image name was incorrect or any other problems for pulling the image
        return Response(data={"details": str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    log = RunLog(application=details)
    log.save()

    try:
        # Run the container
        container_name = details.name + '_' + str(int(datetime.now().timestamp()))
        container = client.containers.run(image=image_name,
                                          name=container_name,
                                          environment=details.envs,
                                          command=details.command,
                                          detach=True)
        log.status = RunLog.Status.FINISHED  # changing status of run log to finished
        log.container_name = container_name
        log.logs = container.logs().decode('utf-8')
        log.save()

        # Count the number of containers with the same image
        num_containers = len([c for c in client.containers.list() if c.image.tags[0] == image_name])
    except Exception as e:
        # Returning 500 if there was any problem for running the container
        log.status = RunLog.Status.FAILED  # changing status of run log to failed
        log.save()
        return Response(data={"details": str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(data={"details": "Successful",
                          "containerName": container_name,
                          "logs": container.logs().decode('utf-8'),
                          "numContainers": num_containers},
                    status=status.HTTP_200_OK)
