from django.db import models

# Create your models here.

# category model provides our products
# with categories like clothing, kitchen & dining etc.
# inherited from models.Model
class Category(models.Model):

    # specifying that plural name for categories
    # is "Categories", not "Categorys" which it
    # set by default
    class Meta:
        verbose_name_plural = "Categories";

    # programmatic name "bed_bath" etc.
    name = models.CharField(max_length=254)

    # user friendly & readable name
    # null & blank true makes this particular field optional
    friendly_name = models.CharField(max_length=254, null=True, blank=True)

    # method that returns programmatic category name
    def __str__(self):
        return self.name

    # method that returns user friendly category name
    def get_friendly_name(self):
        return self.friendly_name


class Product(models.Model):
    # Is optional and if a category is deleted,
    # the products that use this category will have it's
    # category field set to nul instead of being deleted
    category = models.ForeignKey("Category",
                                 null=True,
                                 blank=True,
                                 on_delete=models.SET_NULL)

    sku = models.CharField(max_length=254, null=True, blank=True)
    name = models.CharField(max_length=254)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    rating = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name