from rest_framework import mixins, viewsets


class CreateListDestroyViewSet(mixins.CreateModelMixin,
                               mixins.ListModelMixin,
                               mixins.DestroyModelMixin,
                               mixins.RetrieveModelMixin,
                               viewsets.GenericViewSet):
    pass
