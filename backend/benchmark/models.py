from django.db import models
import uuid

class BenchmarkResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    instance_name = models.CharField(max_length=100)
    run_date = models.DateTimeField(auto_now_add=True)
    time_limit = models.IntegerField(default=15)
    
    # Store the entire results dictionary as JSON
    # This allows flexibility for different types of metrics/coordinates
    results_json = models.JSONField()
    
    class Meta:
        ordering = ['-run_date']
        get_latest_by = 'run_date'
        db_table = 'benchmark_results'

    def __str__(self):
        return f"{self.instance_name} - {self.run_date}"
