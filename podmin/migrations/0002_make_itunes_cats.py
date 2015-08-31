# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def add_categories(apps, schema_editor):
    Category = apps.get_model("podmin", "Category")

    """
    Let's be real here, we need to add a ton of nested categories,
    and we really shouldn't depend on an external (changeable) file
    for this data. We're going to add them all explicitely here,
    tedious as that is. Let's do this once and once only, all future
    Category changes should happen via the app interface, and if any
    categories at all already exist, skip this.

    We are going to have faith in the auto-incrementer here
    and assume we know what the ids of these are going to be.
    """

    if Category.objects.count() != 0:
        return

    itunes_categories = [
        {'name': 'Arts', 'subcats': [
            {'name': 'Design'},
            {'name': 'Fashion & Beauty'},
            {'name': 'Food'},
            {'name': 'Literature'},
            {'name': 'Performing Arts'},
            {'name': 'Visual Arts'},
            ]
        },
        {'name': 'Business', 'subcats': [
            {'name': 'Business News'},
            {'name': 'Careers'},
            {'name': 'Investing'},
            {'name': 'Management &amp Marketing'},
            {'name': 'Shopping'},
            ]
        },
        {'name': 'Comedy', 'subcats': []},
        {'name': 'Education', 'subcats': [
            {'name': 'Education'},
            {'name': 'Education Technology'},
            {'name': 'Higher Education'},
            {'name': 'K-12'},
            {'name': 'Language Courses'},
            {'name': 'Training'},
            ]
        },
        {'name': 'Games & Hobbies', 'subcats': [
            {'name': 'Automotive'},
            {'name': 'Aviation'},
            {'name': 'Hobbies'},
            {'name': 'Other Games'},
            {'name': 'Video Games'},
            ]
        },
        {'name': 'Government & Organizations', 'subcats': [
            {'name': 'Local'},
            {'name': 'National'},
            {'name': 'Non-Profit'},
            {'name': 'Regional'},
            ]
        },
        {'name': 'Health', 'subcats': [
            {'name': 'Alternative Health'},
            {'name': 'Fitness & Nutrition'},
            {'name': 'Self-Help'},
            {'name': 'Sexuality'},
            ]
        },
        {'name': 'Kids & Family', 'subcats': []},
        {'name': 'Music', 'subcats': []},
        {'name': 'News & Politics', 'subcats': []},
        {'name': 'Religion & Spirituality', 'subcats': [
            {'name': 'Buddhism'},
            {'name': 'Christianity'},
            {'name': 'Hinduism'},
            {'name': 'Islam'},
            {'name': 'Judaism'},
            {'name': 'Other'},
            {'name': 'Spirituality'},
            ]
        },
        {'name': 'Science & Medicine', 'subcats': [
            {'name': 'Medicine'},
            {'name': 'Natural Sciences'},
            {'name': 'Social Sciences'},
            ]
        },
        {'name': 'Society & Culture', 'subcats': [
            {'name': 'History'},
            {'name': 'Personal Journals'},
            {'name': 'Philosophy'},
            {'name': 'Places & Travel'},
            ]
        },
        {'name': 'Sports & Recreation', 'subcats': [
            {'name': 'Amateur'},
            {'name': 'College & High School'},
            {'name': 'Outdoor'},
            {'name': 'Professional'},
            ]
        },
        {'name': 'Technology', 'subcats': [
            {'name': 'Gadgets'},
            {'name': 'Tech News'},
            {'name': 'Podcasting'},
            {'name': 'Software How-To'},
            ]
        },
        {'name': 'TV & Film', 'subcats': []},
    ]

    for cat in itunes_categories:
        category = Category(name=cat['name'], itunes=True)
        category.save()
        try:
            for subcat in cat['subcats']:
                subcategory = Category(name=subcat['name'],
                                       parent=category,
                                       itunes=True)
                subcategory.save()
        except:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('podmin', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_categories),
    ]
