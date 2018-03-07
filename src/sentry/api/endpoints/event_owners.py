from __future__ import absolute_import

from rest_framework.response import Response

from sentry.api.bases.project import ProjectEndpoint
from sentry.api.fields.actor import Actor
from sentry.api.serializers import serialize
from sentry.api.serializers.models.actor import ActorSerializer
from sentry.models import Event, ProjectOwnership


class EventOwnersEndpoint(ProjectEndpoint):
    def get(self, request, project, event_id):
        """
        Retrieve suggested owners information for an event
        ``````````````````````````````````````````````````

        :pparam string project_slug: the slug of the project the event
                                     belongs to.
        :pparam string event_id: the id of the event.
        :auth: required
        """
        try:
            event = Event.objects.get(
                id=event_id,
                project_id=project.id,
            )
        except Event.DoesNotExist:
            return Response({'detail': 'Event not found'}, status=404)

        # populate event data
        Event.objects.bind_nodes([event], 'data')

        try:
            ownership = ProjectOwnership.objects.get(project=project)
        except ProjectOwnership.DoesNotExist:
            ownership = ProjectOwnership(
                project=project,
                date_created=None,
                last_updated=None,
            )

        data = {
            'owners': serialize(Actor.resolve_many(
                ownership.get_owners(event)
            ), request.user, ActorSerializer()),
        }
        return Response(data)
