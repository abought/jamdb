from jam.auth import Permissions
from jam.server.api.v1.base import View
from jam.server.api.v1.base import Serializer
from jam.server.api.v1.base import Relationship
from jam.server.api.v1.namespace import NamespaceView
from jam.server.api.v1.search import SearchRelationship
from jam.server.api.v1.namespace import NamespaceSerializer


class CollectionView(View):

    name = 'collection'
    plural = 'collections'
    parent = NamespaceView

    @classmethod
    def load(self, id, namespace):
        return namespace.get_collection(id)

    def __init__(self, namespace, resource=None):
        super().__init__(namespace, resource=resource)
        self._namespace = namespace

    def get_permissions(self, request):
        if not self.resource:
            if request.method == 'GET':
                return Permissions.NONE
            return Permissions.ADMIN
        return super().get_permissions(request)

    def do_create(self, id, attributes, user):
        # TODO Better validation
        if set(attributes.keys()) - {'logger', 'storage', 'state', 'permissions', 'schema'}:
            raise Exception()
        self._namespace.create_collection(id, user.uid, **attributes)
        return self._namespace.read(id)

    def read(self, user):
        return self._namespace.read(self.resource.name)

    def update(self, patch, user):
        return self._namespace.update(self.resource.name, patch, user.uid)


class NamespaceRelationship(Relationship):

    @classmethod
    def view(cls, namespace, collection):
        return NamespaceView(namespace)

    @classmethod
    def serializer(cls):
        return NamespaceSerializer

    @classmethod
    def self_link(cls, request, inst, namespace):
        if request.path.startswith('/v1/id'):
            return '{}://{}/v1/id/namespaces/{}'.format(request.protocol, request.host, namespace.name)
        return '{}://{}/v1/namespaces/{}'.format(request.protocol, request.host, namespace.name)

    @classmethod
    def related_link(cls, request, inst, namespace):
        if request.path.startswith('/v1/id'):
            return '{}://{}/v1/id/namespaces/{}'.format(request.protocol, request.host, namespace.name)
        return '{}://{}/v1/namespaces/{}'.format(request.protocol, request.host, namespace.name)


class DocumentsRelationship(Relationship):

    @classmethod
    def view(cls, namespace, collection):
        from jam.server.api.v1.document import DocumentView
        return DocumentView(namespace, collection)

    @classmethod
    def serializer(cls):
        from jam.server.api.v1.document import DocumentSerializer
        return DocumentSerializer

    @classmethod
    def self_link(cls, request, collection, namespace):
        if request.path.startswith('/v1/id'):
            return '{}://{}/v1/id/collections/{}/documents'.format(request.protocol, request.host, '.'.join((namespace.ref, collection.ref)))
        return '{}://{}/v1/namespaces/{}/collections/{}/documents'.format(request.protocol, request.host, namespace.name, collection.ref)

    @classmethod
    def related_link(cls, request, collection, namespace):
        if request.path.startswith('/v1/id'):
            return '{}://{}/v1/id/collections/{}/documents'.format(request.protocol, request.host, '.'.join((namespace.ref, collection.ref)))
        return '{}://{}/v1/namespaces/{}/collections/{}/documents'.format(request.protocol, request.host, namespace.name, collection.ref)


class CollectionSerializer(Serializer):
    type = 'collections'

    relations = {
        '_search': SearchRelationship,
        'namespace': NamespaceRelationship,
        'documents': DocumentsRelationship,
    }

    @classmethod
    def attributes(cls, inst):
        return {
            'name': inst.ref,
            'schema': inst.data.get('schema'),
            # 'documentCreatorPermissions': Permissions(inst.data['documentCreatorPermissions']).name,
            'permissions': {
                sel: Permissions(perm).name
                for sel, perm in inst.data['permissions'].items()
            }
        }
