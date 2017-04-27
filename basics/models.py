from __future__ import unicode_literals

from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


class Document(models.Model):
    date = models.DateField(verbose_name=_("date of session"))
    legislative_period = models.IntegerField(verbose_name=_("legislative period"))
    document_id = models.IntegerField(verbose_name=_("document per period"))
    url = models.CharField(max_length=250, default=None, null=True)


    def __unicode__(self):
        return "%s/%s (%s)" % (self.legislative_period, self.document_id, self.date)

    def link_decorator(self):
        return reverse("basics:document", args=(self.document_id,))

class Party(models.Model):

    name = models.CharField(max_length=200, verbose_name=_("party name"), blank=True, default="")
    abbrev = models.CharField(max_length=200, verbose_name=_("abbreviation"))

    def __unicode__(self):
        return "%s" % self.abbrev

    def num_statements_decorator(self):
        return RegularStatement.objects.filter(speaker__party=self).count()

    def link_decorator(self):
        return reverse("basics:party", args=(self.pk,))


class Function(models.Model):

    name = models.CharField(max_length=200, verbose_name=_("function name"))

    def __unicode__(self):
        return "%s" % self.name

    def num_statements_decorator(self):
        return RegularStatement.objects.filter(speaker__function=self).count()

    def link_decorator(self):
        return reverse("basics:function", args=(self.pk,))


class StmtBlock(models.Model):

    stmt_block_no = models.IntegerField(verbose_name=_("no of statement_block continuous"))
    speaker = models.ForeignKey("basics.Speaker", verbose_name=_("who said it"), default=None, null=True)
    document = models.ForeignKey("basics.Document", verbose_name=_("who said it"), default=None, null=True)


class RegularStatement(models.Model):

    text = models.TextField(verbose_name=_("text"))
    str_adjectives = models.TextField(verbose_name=_("standardized adjectives"), default=None)
    str_nouns = models.TextField(verbose_name=_("standardized nouns"), default=None)
    str_verbs = models.TextField(verbose_name=_("standardized verbs"), default=None)
    str_partizip_i = models.TextField(verbose_name=_("standardized partizip i"), default=None, null=True)
    str_other_words = models.TextField(verbose_name=_("other words"), default=None)
    str_persons = models.TextField(verbose_name=_("persons"), default=None)
    str_titles = models.TextField(verbose_name=_("wikipedia titles"), default=None)
    speaker = models.ForeignKey("basics.Speaker", verbose_name=_("who said it"))
    document = models.ForeignKey("basics.Document", verbose_name=_("source document"), default=None)
    order_id = models.IntegerField(verbose_name=_("order within document"), default=0)
    stmt_block_no = models.ForeignKey("basics.StmtBlock", verbose_name=_("block of statements that where uttered by one speaker directly after another"), default=0)
    no_unique_words = models.IntegerField(verbose_name=_('number of unique standardized words of the statement'), default=0)
    page = models.IntegerField(verbose_name=_("page where statement begins"), default=0)
    cleaned_text = models.TextField(verbose_name=_("only letters"), default=None, null=True)

    def __unicode__(self):
        return "%s-%s %s" % (self.document, self.order_id, self.speaker)

    def text_short_decorator(self):
        return self.text[:30]

    def str_nouns_short_decorator(self):
        return self.str_nouns[:30]

class Speaker(models.Model):

    name = models.CharField(max_length=200, verbose_name=_("speaker name"))
    party = models.ForeignKey("basics.Party", on_delete=models.CASCADE)
    function = models.ForeignKey("basics.Function", on_delete=models.CASCADE)

    def __unicode__(self):
        if self.party.abbrev:
            return "%s (%s)" % (self.name, self.party.abbrev)
        else:
            return "%s (%s)" % (self.name, self.function)


    def link_decorator(self):
        return reverse("basics:speaker", args=(self.pk, ))

    def number_of_statements_decorator(self):
        return RegularStatement.objects.filter(speaker=self).count()

class Statistics(models.Model):
    no_plenarprotokolle = models.IntegerField(verbose_name=_("How many Plenarprotokolle in db"), default=0)
    no_speakers = models.IntegerField(verbose_name=_("How many speakers"), default=0)
    no_functions = models.IntegerField(verbose_name=_("How many functions"), default=0)
    no_parties = models.IntegerField(verbose_name=_("How many Parties"), default=0)


'''class SpeakerStatistics(models.Model):
    speaker = models.ForeignKey("basics.Speaker", verbose_name=_("whose statistics"))
    no_statements = models.IntegerField(verbose_name=_("number of statements"))
    no_words = models.IntegerField(verbose_name=_("number of words"))
    no_statement_blocks = models.IntegerField(verbose_name=("number of statement blocks"))
    percent_of_words = models.FloatField(verbose_name=("percent of all words in leg period by speaker"))
    no_of_long_statement_blocks = models.IntegerField(verbose_name=("number of statement blocks which have more than 4 statements"))
    active_leg_periods = models.TextField(verbose_name=_("active legislative periods"))
    active_documents_ordered = models.IntegerField(verbose_name=("number of statement blocks ordered by number of statements"))'''
