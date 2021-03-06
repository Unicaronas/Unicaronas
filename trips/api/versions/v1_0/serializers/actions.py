from rest_framework import serializers


class DriverActionsSerializer(serializers.Serializer):
    action = serializers.ChoiceField(
        label="Ação a ser realizada no passageiro",
        choices=(('approve', 'Aprovar'),
                 ('deny', 'Negar'), ('forfeit', 'Remover')),
        required=True
    )


class FuturePassengerActionsSerializer(serializers.Serializer):
    action = serializers.ChoiceField(
        label="Ação a ser realizada na carona",
        choices=(('book', 'Entrar na carona'),),
        required=True
    )
    seats = serializers.IntegerField(
        label='Número de assentos a reservar',
        required=False,
        min_value=1,
        max_value=10
    )


class PassengerActionsSerializer(serializers.Serializer):
    action = serializers.ChoiceField(
        label="Ação a ser realizada pelo passageiro",
        choices=(('give_up', 'Desistir da carona'),),
        required=True
    )
