#############################################################################
#                                                                           #
#    Copyright (C) 2007 William Waites <ww@styx.org>                        #
#                                                                           #
#    This program is free software; you can redistribute it and#or modify   #
#    it under the terms of the GNU General Public License as                #
#    published by the Free Software Foundation; either version 2 of the     #
#    License, or (at your option) any later version.                        #
#                                                                           #
#    This program is distributed in the hope that it will be useful,        #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#    GNU General Public License for more details.                           #
#                                                                           #
#    You should have received a copy of the GNU General Public              #
#    License along with this program; if not, write to the                  #
#    Free Software Foundation, Inc.,                                        #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.              #
#                                                                           #
#############################################################################
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

__all__ = ['Currency']

class CurrencyManager(models.Manager):
	def quote(self, buy, sell, timestamp = None):
		"""
		## Return the value of one unit of sell currency in
		## the buy currency at the given time.
		##
		## timestamp defaults to now
		##
		## example:
		>>>
		>>> print Currency.objects.quote('EUR', 'CAD', '2007-01-01')
		>>>
		"""
		from datetime import datetime
		if not timestamp:
			timestamp = datetime.now()

		sellfilter = { 'timestamp__lte' : timestamp }
		if isinstance(sell, Currency): sellfilter['currency'] = sell
		else: sellfilter['currency__code'] = str(sell)

		buyfilter = { 'timestamp__lte' : timestamp }
		if isinstance(buy, Currency): buyfilter['currency'] = buy
		else: buyfilter['currency__code'] = str(buy)

		try:
			sell_exchange = ExchangeRate.objects.filter(**sellfilter).latest("timestamp")
			buy_exchange = ExchangeRate.objects.filter(**buyfilter).latest("timestamp")
		except ExchangeRate.DoesNotExist, e:
			raise self.model.DoesNotExist, e

		return buy_exchange / sell_exchange

	def set(self, currency, rate, timestamp):
		if not isinstance(currency, self.model):
			currency, created = self.get_or_create(code = str(currency),
								description = str(currency))
		exchange, created = ExchangeRate.objects.get_or_create(currency = currency,
								timestamp = timestamp,
								exchange = rate)
		return exchange

	def default(self):
		return self.model.get(code = settings.DEFAULT_CURRENCY)

class Currency(models.Model):
        class Admin:
                list_display = ('code', 'description')
        class Meta:
                verbose_name = _('Currency')
                verbose_name_plural = _('Currencies')
		ordering = ('code',)
	objects = CurrencyManager()
        code = models.CharField(maxlength = 4, unique = True, verbose_name = _('Code'))
	description = models.CharField(maxlength = 32, verbose_name = _('Description'))
        def __str__(self):
                return self.code

class ExchangeRate(models.Model):
	class Meta:
		verbose_name = _('Exchange Rate')
		verbose_name_plural = _('Exchange Rates')
		ordering = ('-timestamp',)
	timestamp = models.DateTimeField(core = True)
	currency = models.ForeignKey(Currency, edit_inline = True, related_name = 'rates', verbose_name = _('Currency'))
        exchange = models.DecimalField(max_digits=12, decimal_places=8, verbose_name = _('Exchange Rate'))
        def __float__(self):
                return float(self.exchange)
	def __div__(self, other):
		return self.exchange / other.exchange
