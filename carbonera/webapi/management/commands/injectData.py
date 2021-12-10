from django.core.management.base import BaseCommand, CommandError, CommandParser
from webapi.models import Unit, Item, Category
from dataparsing.ademeParser import AdemeParser 
from django.core.exceptions import MultipleObjectsReturned

class Command(BaseCommand):
    help = "Injects initial ademe data into database"

    def handle(self, *args, **options):
        parser = AdemeParser()
        parser.parse()
        self.stdout.write('Inserting Unit data')
        modelUnits = [
            Unit(
                name=dict.get('name'),
                numerator=dict.get('numerator'),
                denominator=dict.get('denominator')) 
            for dict in parser.carbonUnits]

        unitObjects = Unit.objects.bulk_create(modelUnits)
        self.stdout.write(self.style.SUCCESS(f'Created {len(unitObjects)} model units'))
        
        self.stdout.write('Inserting category data')
        for dict in parser.carbonCategories:        
            categoryName = dict.get('name')

            elderCategoryName = dict.get('parent')
            elderCategory = None
            if elderCategoryName:
                elderCategory = Category.objects.filter(name=elderCategoryName).order_by('-pk').first()

            try:
                parentCategory = Category.objects.get(name=categoryName, parent=elderCategory)
            except Category.DoesNotExist:
                parentCategory = Category.objects.create(name=categoryName, parent=elderCategory)    

            for sub in dict.get('subCategories'):
                Category.objects.create(name=sub, parent=parentCategory)

        self.stdout.write(self.style.SUCCESS(f'Created {Category.objects.all().count} category data'))

        self.stdout.write('Inserting carbon Item data')

        modelItems = []
        for entry in parser.carbonDb:
            
            unitObject = Unit.objects.get(name=entry.get('unite_francais'))
            splitCategories = entry.get('code_de_la_categorie').lower().strip().split('>')
            elder = splitCategories[0].strip()
            categoryName = splitCategories[-1].strip()
            parentCategoryName = splitCategories[-2].strip()

            # Some categories have parents and n-1 parents that are similar, we can de-dup by using the original node.
            try:
                catObject = Category.objects.get(name=categoryName, parent__name=parentCategoryName)
            except MultipleObjectsReturned:
                cats = Category.objects.filter(name=categoryName, parent__name=parentCategoryName)
                for c in cats:
                    if c.ancestors()[0].name == elder:
                        catObject = c
            it = Item(
                name_fr=entry.get('nom_base_francais'),
                name_en=entry.get('nom_base_anglais'),
                attribute_fr=entry.get('nom_attribut_francais'),
                attribute_en=entry.get('nom_attribut_anglais'),
                category_str=entry.get('code_de_la_categorie'),
                tag_fr=entry.get('tags_francais'),
                tag_en=entry.get('tags_anglais'),
                unit_str=entry.get('unite_francais'),
                confidence=entry.get('incertitude'),
                total_poste=entry.get('total_poste_non_decompose'),
                co2f=entry.get('co2f'),
                ch4f=entry.get('ch4f'),
                ch4b=entry.get('ch4b'),
                n2o=entry.get('n2o'),
                co2b=entry.get('co2b'),
                other_ghg=entry.get('autres_ges'),
                unit=unitObject,
                category=catObject
                )
            
            modelItems.append(it)

        itemObjects = Item.objects.bulk_create(modelItems)
        self.stdout.write(self.style.SUCCESS(f'Created {len(itemObjects)} model Items'))

        self.stdout.write(self.style.SUCCESS('Successfully added Data to database'))