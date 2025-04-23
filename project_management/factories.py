from factory import Faker, SubFactory, post_generation
from factory.django import DjangoModelFactory

from authentication.factories import UserFactory
from authentication.models import User
from project_management.models import Feature, Function, Project, WorkLog


class ProjectFactory(DjangoModelFactory):
    title = Faker("sentence")
    description = Faker("text")
    client = SubFactory(UserFactory, role=User.Role.CLIENT)
    start_date = Faker("date_time")

    class Meta:
        model = Project

    @post_generation
    def developers(self, create, extracted, **kwargs):
        """
        Add developers after project creation.
        - If extracted (passed explicitly), use that list.
        - Otherwise, create a random number (e.g., 2) of developers.
        """
        if not create:
            return  # Skip for "build" strategy

        if extracted:
            for developer in extracted:
                self.developers.add(developer)
        else:
            devs = UserFactory.create_batch(2, role=User.Role.DEVELOPER)
            self.developers.add(*devs)


class FeatureFactory(DjangoModelFactory):
    project = SubFactory(ProjectFactory)
    title = Faker("sentence")
    description = Faker("sentence")

    class Meta:
        model = Feature


class FunctionFactory(DjangoModelFactory):
    title = Faker("sentence")
    description = Faker("sentence")
    developer = SubFactory(UserFactory, role=User.Role.DEVELOPER)
    feature = SubFactory(FeatureFactory)

    class Meta:
        model = Function


class WorkLogFactory(DjangoModelFactory):
    project = SubFactory(ProjectFactory)
    developer = SubFactory(UserFactory, role=User.Role.DEVELOPER)
    function = SubFactory(FunctionFactory)
    hours_worked = Faker("pyint", min_value=1, max_value=10)
    date_logged = Faker("date_time")

    class Meta:
        model = WorkLog
