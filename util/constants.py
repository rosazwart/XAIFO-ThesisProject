# Dependent on BioLink API responses defined at https://api.monarchinitiative.org/api/
# `_` indicates dictionary key level separation for example `dict['subject']['id']`
assoc_tuple_values = ('id', 
                      'subject_id', 'subject_label', 'subject_iri', 'subject_category', 'subject_taxon_id', 'subject_taxon_label',
                      'object_id', 'object_label', 'object_iri', 'object_category', 'object_taxon_id', 'object_taxon_label', 
                      'relation_id', 'relation_label', 'relation_iri')

GENOTYPE = 'genotype'
GENE = 'gene'
TAXON = 'taxon'
DRUG = 'drug'
DISEASE = 'disease'
PHENOTYPE = 'phenotype'

INPUT_FOLDER = 'data'
OUTPUT_FOLDER = 'output'