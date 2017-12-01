from datetime import timedelta

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ztc.utils.stuff_date import parse_onvolledige_datum
from ..choices import JaNee
from .mixins import GeldigheidMixin


class CheckListItem(models.Model):
    """
    Te controleren aandachtspunt voorafgaand aan het bereiken van een status van het STATUSTYPE.

    Door één of meer checklistitems op te nemen bij een status, wordt een checklist verkregen met
    punten waaraan aandacht besteed moet worden teneinde die status te bereiken.

    # TODO: wanneer sub attributeen op een StatusType worden gegeven, dient er dan een nieuwe instance van
    checklistItem te worden gemaakt?
    """
    itemnaam = models.CharField(_('itemnaam'), max_length=30, help_text=_(
        'De betekenisvolle benaming van het checklistitem'))
    vraagstelling = models.CharField(_('vraagstelling'), max_length=255, help_text=_(
        'Een betekenisvolle vraag waaruit blijkt waarop het aandachtspunt gecontroleerd moet worden.'))
    # verplicht is gedefinieerd als BooleanField, en informeren als AN1, beide met waardeverzameling J/N
    verplicht = models.CharField(_('verplicht'), max_length=1, choices=JaNee.choices, help_text=_(
        'Het al dan niet verplicht zijn van controle van het aandachtspunt voorafgaand aan het bereiken van de '
        'status van het gerelateerde STATUSTYPE.'))
    toelichting = models.CharField(_('toelichting'), max_length=1000, blank=True, null=True, help_text=_(
        'Beschrijving van de overwegingen bij het controleren van het aandachtspunt'))


class StatusType(GeldigheidMixin, models.Model):
    """
    Generieke aanduiding van de aard van een STATUS

    Toelichting objecttype
    Zaken van eenzelfde zaaktype doorlopen alle dezelfde statussen, tenzij de zaak voortijdig
    beeëindigd wordt. Met STATUSTYPE worden deze statussen benoemd bij het desbetreffende
    zaaktype. De attribuutsoort ‘Doorlooptijd status’ is niet bedoeld om daarmee voor een
    individuele zaak de statussen te plannen maar om geïnteresseerden informatie te verschaffen
    over de termijn waarop normaliter een volgende status bereikt wordt.
    """
    statustype_omschrijving = models.CharField(_('statustype omschrijving'), max_length=80, help_text=_(
        'Een korte, voor de initiator van de zaak relevante, omschrijving van de aard van de STATUS van zaken van een ZAAKTYPE.'))
    statustype_omschrijving_generiek = models.CharField(
        _('statustype omschrijving generiek'), max_length=80, blank=True, null=True,
        help_text=_('Algemeen gehanteerde omschrijving van de aard van STATUSsen van het STATUSTYPE'))
    # waardenverzameling is 0001 - 9999, omdat int('0001') == 1 als PositiveSmallIntegerField
    statustypevolgnummer = models.PositiveSmallIntegerField(
        _('statustypevolgnummer'), validators=[MinValueValidator(1), MaxValueValidator(9999)], help_text=_(
            'Een volgnummer voor statussen van het STATUSTYPE binnen een zaak.'))
    doorlooptijd_status = models.PositiveSmallIntegerField(
        _('doorlooptijd status'), blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(999)],
        help_text=_('De door de zaakbehandelende organisatie(s) gestelde norm voor de doorlooptijd voor het bereiken '
                    'van statussen van dit STATUSTYPE bij het desbetreffende ZAAKTYPE, vanaf het bereiken van de voorafgaande status'))
    checklistitem = models.ManyToManyField(
        'datamodel.CheckListItem', verbose_name=_('checklistitem'), blank=True, help_text=_(
            'Te controleren aandachtspunt voorafgaand aan het bereiken van een status van het STATUSTYPE.'))
    informeren = models.CharField(_('informeren'), max_length=1, choices=JaNee.choices, help_text=_(
        'Aanduiding die aangeeft of na het zetten van een STATUS van dit STATUSTYPE de Initiator moet worden geïnformeerd over de statusovergang.'))
    statustekst = models.CharField(_('statustekst'), max_length=1000, blank=True, null=True,
        help_text=_('De tekst die wordt gebruikt om de Initiator te informeren over het bereiken van een STATUS van dit STATUSTYPE bij het desbetreffende ZAAKTYPE.'))
    toelichting = models.CharField(_('toelichting'), max_length=1000, blank=True, null=True, help_text=_(
        'Een eventuele toelichting op dit STATUSTYPE.'))

    # TODO: deze 3 relaties zijn STATUSTYPE [0..1] ... [0..*], en vat ik op alsof de relatie beter andersom gelegt kan worden
    # heeft_verplichte   optionele foreignkey op Zaak-InformatieobjectType  (related_name='heeft_verplichte_zit') ?
    # heeft_verplichte   optionele foreignkey op Eigenschap  (related_name='heeft_verplichte_eigenschap') ?
    # heeft_verplichte   optionele foreignkey op ZaakObjectType  (related_name='heeft_verplichte_zaakobjecttype') ?

    # TODO:
    # is_van = models.ForeignKey('datamodel.ZaakType', verbose_name=_('is van'), help_text=_(
    #     'Het ZAAKTYPE van ZAAKen waarin STATUSsen van dit STATUSTYPE bereikt kunnen worden.'))

    class Meta:
        mnemonic = 'STT'
        # TODO: als is_van relatie bestaat
        # unique_together = ('is_van', 'statustypevolgnummer')

    def clean(self):
        """
        datum_begin_geldigheid:
        - De datum is gelijk aan een Versiedatum van het gerelateerde zaaktype.

        datum_einde_geldigheid:
        - De datum is gelijk aan of gelegen na de datum zoals opgenomen onder 'Datum begin geldigheid statusType’.
        - De datum is gelijk aan de dag voor een Versiedatum van het gerelateerde zaaktype.
        """
        datum_begin = parse_onvolledige_datum(self.datum_begin_geldigheid)
        versiedatum = parse_onvolledige_datum(self.is_van.versiedatum)

        if datum_begin != versiedatum:
            raise ValidationError(
                _("De datum_begin_geldigheid moet gelijk zijn aan een Versiedatum van het gerelateerde zaaktype."))

        if self.datum_einde_geldigheid:
            datum_einde = parse_onvolledige_datum(self.datum_einde_geldigheid)

            if datum_einde < datum_begin:
                raise ValidationError(_(
                    "'Datum einde geldigheid' moet gelijk zijn aan of gelegen na de datum zoals opgenomen onder 'Datum begin geldigheid’"))

            if datum_einde + timedelta(days=1) != versiedatum:
                raise ValidationError(_(
                    "'Datum einde geldigheid' moet gelijk zijn aan de dag voor een Versiedatum van het gerelateerde zaaktype."))
