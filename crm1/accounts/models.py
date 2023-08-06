from django.db import models
from django.contrib.auth.models import User

class Tag(models.Model):
    tag = models.CharField(max_length=200, null=True)
    # Tag table is dependent on nothing. Can exist solely.

    def __str__(self) -> str:
        return self.tag


class Customer(models.Model):
    user= models.OneToOneField(User, on_delete=models.CASCADE,null=True, blank=True) #dropdown, but unique singpular relationship
    name = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=100, null=True)
    email = models.CharField(max_length=200, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    profile_pic=models.ImageField(null=True,default='profile1.png',blank=True) #blank = true means image field can be left blank
    # Customer table is dependent on nothing. Can exist solely.

    def __str__(self) -> str:
        return self.name


class Products(models.Model):
    CATEGORY = (
        ('Indoor', 'Indoor'),
        ('Out Door', 'Out Door'),
    )
    name = models.CharField(max_length=200, null=True)
    price = models.FloatField(null=True)
    description = models.CharField(max_length=200, null=True)
    category = models.CharField(max_length=200, null=True, choices=CATEGORY)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    # Product table is dependent on tag. Can't exist solely.
    # 1 Product will have many tags, 1 tag will have many products. Many to Many, Repr. by Multiple Choice Dropdown
    tags = models.ManyToManyField(Tag)
    #trick: we want mcq option 
    # Product properies is independent to customers, orders but dependent on tags
    def __str__(self):
        return str(self.name)


class Order(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Out for delivery', 'Out for delivery'),
        ('Delivered', 'Delivered'),
    )
    # Order table is dependent on customer,product. Can't exist solely.
    # Order properies is dependent to customers, orders but not dependent on tags
    # 1 Order will have a customer , and product as two main info. Use foreign key to differentiate. Drop Down repr.
    # Order | Customer | Product |
    # 0231    Philip      Ball
    # 1 customer can have many orders. One to Many.
    customer = models.ForeignKey(
        Customer, null=True, on_delete=models.SET_NULL)
    # 1 product can have many orders. One to Many, trick: we want dropdown showing many customers
    product = models.ForeignKey(Products, null=True, on_delete=models.SET_NULL)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    status = models.CharField(max_length=200, null=True, choices=STATUS)

    def __str__(self):
        return self.product.name
    