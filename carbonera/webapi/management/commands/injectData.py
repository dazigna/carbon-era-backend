from django.core.management.base import BaseCommand, CommandError, CommandParser
from webapi.models import Unit, Item, Category
from dataparsing.ademeParser import AdemeParser 

class Command(BaseCommand):
    help = "Injects initial ademe data into database"

    def handle(self, *args, **options):
        parser = AdemeParser()
        parser.parse()
        # self.stdout.write('Inserting Unit data')
        # modelUnits = [
        #     Unit(
        #         name=dict.get('name'),
        #         numerator=dict.get('numerator'),
        #         denominator=dict.get('denominator')) 
        #     for dict in parser.carbonUnits]

        # unitObjects = Unit.objects.bulk_create(modelUnits)
        # self.stdout.write(self.style.SUCCESS(f'Created {len(unitObjects)} model units'))

        self.stdout.write('Inserting category data')
        for dict in parser.carbonCategories:
            # if not dict.get('subCategories'):
            #     continue
            # try:
            #     cat = Category.objects.get(name=dict.get('name'))
            # except Category.DoesNotExist:
            #     cat = Category(name=dict.get('name'))
            #     cat.save()
            

            if not dict.get('subCategories'):
                continue
            categoryName = dict.get('name')
            # (parentCategory, didCreate) = Category.objects.get_or_create(name=categoryName)
            parentCategory = Category(name=categoryName)
            parentCategory.save()
            print(f'Did create cat {categoryName}')

            for sub in dict.get('subCategories'):
                print(f'Creating sub cat {sub} for cat {parentCategory.name} {parentCategory.pk}')
                Category(name=sub, parent=parentCategory.pk).save()
                print(f'Did create sub cat {categoryName}')

    
        self.stdout.write(self.style.SUCCESS(f'Created {Category.objects.all().count} category data'))

        # # TODO: Missing foreign key to units and categories
        # self.stdout.write('Inserting carbon Item data')
        # modelItems = [
        #     Item(
        #         name_fr=dict.get('nom_base_francais'),
        #         name_en=dict.get('nom_base_anglais'),
        #         attribute_fr=dict.get('nom_attribut_francais'),
        #         attribute_en=dict.get('nom_attribut_anglais'),
        #         category_str=dict.get('code_de_la_categorie'),
        #         tag_fr=dict.get('tags_francais'),
        #         tag_en=dict.get('tags_anglais'),
        #         unit_str=dict.get('unite_francais'),
        #         confidence=dict.get('incertitude'),
        #         total_poste=dict.get('total_poste_non_decompose'),
        #         co2f=dict.get('co2f'),
        #         ch4f=dict.get('ch4f'),
        #         ch4b=dict.get('ch4b'),
        #         n2o=dict.get('n2o'),
        #         co2b=dict.get('co2b'),
        #         other_ghg=dict.get('autres_ges'))
        #      for dict in parser.carbonDb]

        # itemObjects = Item.objects.bulk_create(modelItems)
        # self.stdout.write(self.style.SUCCESS(f'Created {len(itemObjects)} model Items'))

        self.stdout.write(self.style.SUCCESS('Successfully added Data to database'))