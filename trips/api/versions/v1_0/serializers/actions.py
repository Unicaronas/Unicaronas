from rest_framework import serializers


class DriverActionsSerializer(serializers.Serializer):
    action = serializers.ChoiceField(
        label="Ação a ser realizada no passageiro",
        choices=(('approve', 'Aprovar'),
                 ('deny', 'Negar'), ('forfeit', 'Remover'))
    )
