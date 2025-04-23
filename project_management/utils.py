from datetime import datetime


def generate_financial_data_for_client(project, user):
    pass


def get_developer_rate(*, project, developer):
    from project_management.models import ProjectRate

    project_rate = ProjectRate.objects.filter(project=project, developer=developer)
    if not project_rate.exists():
        return 0
    return project_rate.first().rate
