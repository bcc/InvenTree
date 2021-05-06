"""
JSON serializers for Company app
"""

from rest_framework import serializers

from sql_util.utils import SubqueryCount

from .models import Company
from .models import ManufacturerPart
from .models import SupplierPart, SupplierPriceBreak

from InvenTree.serializers import InvenTreeModelSerializer

from part.serializers import PartBriefSerializer


class CompanyBriefSerializer(InvenTreeModelSerializer):
    """ Serializer for Company object (limited detail) """

    url = serializers.CharField(source='get_absolute_url', read_only=True)

    image = serializers.CharField(source='get_thumbnail_url', read_only=True)

    class Meta:
        model = Company
        fields = [
            'pk',
            'url',
            'name',
            'description',
            'image',
        ]


class CompanySerializer(InvenTreeModelSerializer):
    """ Serializer for Company object (full detail) """

    @staticmethod
    def annotate_queryset(queryset):

        # Add count of parts manufactured
        queryset = queryset.annotate(
            parts_manufactured=SubqueryCount('manufactured_parts')
        )

        queryset = queryset.annotate(
            parts_supplied=SubqueryCount('supplied_parts')
        )

        return queryset

    url = serializers.CharField(source='get_absolute_url', read_only=True)
    
    image = serializers.CharField(source='get_thumbnail_url', read_only=True)

    parts_supplied = serializers.IntegerField(read_only=True)
    parts_manufactured = serializers.IntegerField(read_only=True)

    class Meta:
        model = Company
        fields = [
            'pk',
            'url',
            'name',
            'description',
            'website',
            'name',
            'phone',
            'address',
            'email',
            'contact',
            'link',
            'image',
            'is_customer',
            'is_manufacturer',
            'is_supplier',
            'notes',
            'parts_supplied',
            'parts_manufactured',
        ]


class ManufacturerPartSerializer(InvenTreeModelSerializer):
    """ Serializer for ManufacturerPart object """

    part_detail = PartBriefSerializer(source='part', many=False, read_only=True)

    manufacturer_detail = CompanyBriefSerializer(source='manufacturer', many=False, read_only=True)

    pretty_name = serializers.CharField(read_only=True)

    def __init__(self, *args, **kwargs):

        part_detail = kwargs.pop('part_detail', False)
        manufacturer_detail = kwargs.pop('manufacturer_detail', False)
        prettify = kwargs.pop('pretty', False)

        super(ManufacturerPartSerializer, self).__init__(*args, **kwargs)

        if part_detail is not True:
            self.fields.pop('part_detail')

        if manufacturer_detail is not True:
            self.fields.pop('manufacturer_detail')

        if prettify is not True:
            self.fields.pop('pretty_name')

    manufacturer = serializers.PrimaryKeyRelatedField(queryset=Company.objects.filter(is_manufacturer=True))

    class Meta:
        model = ManufacturerPart
        fields = [
            'pk',
            'part',
            'part_detail',
            'pretty_name',
            'manufacturer',
            'manufacturer_detail',
            'description',
            'MPN',
            'link',
        ]


class SupplierPartSerializer(InvenTreeModelSerializer):
    """ Serializer for SupplierPart object """

    part_detail = PartBriefSerializer(source='part', many=False, read_only=True)

    supplier_detail = CompanyBriefSerializer(source='supplier', many=False, read_only=True)

    manufacturer_detail = CompanyBriefSerializer(source='manufacturer_part.manufacturer', many=False, read_only=True)

    pretty_name = serializers.CharField(read_only=True)

    def __init__(self, *args, **kwargs):

        part_detail = kwargs.pop('part_detail', False)
        supplier_detail = kwargs.pop('supplier_detail', False)
        manufacturer_detail = kwargs.pop('manufacturer_detail', False)
        prettify = kwargs.pop('pretty', False)

        super(SupplierPartSerializer, self).__init__(*args, **kwargs)

        if part_detail is not True:
            self.fields.pop('part_detail')

        if supplier_detail is not True:
            self.fields.pop('supplier_detail')

        if manufacturer_detail is not True:
            self.fields.pop('manufacturer_detail')

        if prettify is not True:
            self.fields.pop('pretty_name')

    supplier = serializers.PrimaryKeyRelatedField(queryset=Company.objects.filter(is_supplier=True))
    
    manufacturer = serializers.PrimaryKeyRelatedField(source='manufacturer_part.manufacturer', read_only=True)
    
    MPN = serializers.StringRelatedField(source='manufacturer_part.MPN')

    manufacturer_part = ManufacturerPartSerializer(read_only=True)

    class Meta:
        model = SupplierPart
        fields = [
            'pk',
            'part',
            'part_detail',
            'pretty_name',
            'supplier',
            'supplier_detail',
            'SKU',
            'manufacturer',
            'MPN',
            'manufacturer_detail',
            'manufacturer_part',
            'description',
            'link',
        ]

    def create(self, validated_data):
        """ Extract manufacturer data and process ManufacturerPart """

        # Create SupplierPart
        supplier_part = super().create(validated_data)

        # Get ManufacturerPart raw data (unvalidated)
        manufacturer_id = self.initial_data.get('manufacturer', None)
        MPN = self.initial_data.get('MPN', None)

        if manufacturer_id and MPN:
            kwargs = {
                'manufacturer': manufacturer_id,
                'MPN': MPN,
            }
            supplier_part.save(**kwargs)

        return supplier_part


class SupplierPriceBreakSerializer(InvenTreeModelSerializer):
    """ Serializer for SupplierPriceBreak object """

    quantity = serializers.FloatField()

    price = serializers.CharField()

    class Meta:
        model = SupplierPriceBreak
        fields = [
            'pk',
            'part',
            'quantity',
            'price',
        ]
