from Products.ATContentTypes.criteria import boolean

from collective.formcriteria.criteria import common

class BooleanFormCriterion(
    common.FormCriterion, boolean.ATBooleanCriterion):
    __doc__ = boolean.ATBooleanCriterion.__doc__

    schema = boolean.ATBooleanCriterion.schema.copy(
        ) + common.FormCriterion.schema.copy()
    schema['bool'].widget.hide_form_label = True
    schema['formFields'].vocabulary = common.makeVocabularyForFields(
        schema['bool'])

common.replaceCriterionRegistration(
    boolean.ATBooleanCriterion, BooleanFormCriterion)
