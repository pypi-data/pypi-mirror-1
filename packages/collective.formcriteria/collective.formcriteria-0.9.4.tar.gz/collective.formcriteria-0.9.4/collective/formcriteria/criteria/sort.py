import Acquisition

from Products.ATContentTypes.criteria import sort

from collective.formcriteria import interfaces
from collective.formcriteria.criteria import common

class ATSortCriterion(
    common.FormCriterion, sort.ATSortCriterion):
    __doc__ = sort.ATSortCriterion.__doc__

    schema = sort.ATSortCriterion.schema.copy()
    shortDesc      = 'Sort results'

    def getCriteriaItems(self):
        """Only use this sort if it is the default or is specified"""
        topic = Acquisition.aq_parent(Acquisition.aq_inner(self))
        if not interfaces.IFormTopic.providedBy(topic) or (
            self.Field() != 'unsorted' and (
                self.getId() in self.REQUEST or
                Acquisition.aq_base(self) is Acquisition.aq_base(
                    topic.listSortCriteria()[0]))):
            return super(ATSortCriterion, self).getCriteriaItems()
        return ()
    

common.replaceCriterionRegistration(sort.ATSortCriterion,
                                    ATSortCriterion)
