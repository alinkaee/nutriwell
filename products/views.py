from django.http import JsonResponse
from .models import Product

def get_product_nutrition(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        return JsonResponse({
            'calories': product.calories_per_100g,
            'protein': float(product.protein_per_100g),
            'fat': float(product.fat_per_100g),
            'carbs': float(product.carbs_per_100g),
        })
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Продукт не найден'}, status=404)