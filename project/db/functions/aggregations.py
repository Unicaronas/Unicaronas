from django.db.models import Count, F, Case, When, Value, IntegerField, FloatField, ExpressionWrapper
from project.db.functions.math import Log, Power, Round


def annotate_final_score(queryset):
    """Take an application queryset
    and calculate the final score using
    Steam's algorithm:
    https://steamdb.info/blog/steamdb-rating/
    """
    queryset = queryset.annotate(
        total_ratings=Count('ratings'),
        positive_ratings=Count(
            Case(
                When(ratings__rating=True, then=1)
            )
        )
    ).annotate(
        score=Case(
            When(total_ratings=0, then=0),
            default=F('positive_ratings') / F('total_ratings')
        ),
        two=Value(2, output_field=IntegerField()),
        ten=Value(10, output_field=IntegerField()),
        bias=Value(0.5, output_field=FloatField())
    ).annotate(
        inner_log=-Log('ten', F('total_ratings') + 1, output_field=FloatField())
    ).annotate(
        power=Power('two', 'inner_log', output_field=FloatField())
    ).annotate(
        normalized_score=ExpressionWrapper(
            (F('score') - (F('score') - F('bias')) * F('power')) * 100,
            output_field=FloatField()
        )
    ).annotate(
        final_score=Round('normalized_score', output_field=IntegerField())
    )
    return queryset
