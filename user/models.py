from django.db    import models

class Country(models.Model):
    name = models.CharField(max_length=16)

    class Meta:
        db_table = "countries"

    def __str__(self):
        return self.name

class User(models.Model):
    name          = models.CharField(max_length=32)
    country       = models.ForeignKey(Country,on_delete=models.CASCADE)
    email         = models.CharField(max_length=32)
    password      = models.CharField(max_length=256)
    nickname      = models.CharField(max_length=16)
    code          = models.CharField(max_length=16)
    profile_image = models.URLField(default="https://i.pinimg.com/474x/34/c2/f9/34c2f984350ed23d1efa7094d7923c5a.jpg", max_length=512, null=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.name