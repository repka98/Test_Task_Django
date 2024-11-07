from rest_framework import serializers

from .models import Application


class ApplicationSerializer(serializers.ModelSerializer):
	user_name = serializers.CharField(source='user_app.name')
	user_last_name = serializers.CharField(source='user_app.last_name')
	user_surname = serializers.CharField(source='user_app.surname')
	hash_data = serializers.CharField(source='hash_data.hash')
	number_app = serializers.CharField(max_length=12)
	created_at = serializers.DateTimeField()
	finished_at = serializers.DateTimeField()

	class Meta:
		model = Application
		fields = '__all__'