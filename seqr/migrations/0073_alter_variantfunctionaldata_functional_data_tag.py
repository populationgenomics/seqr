# Generated by Django 4.2.13 on 2024-08-14 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seqr', '0072_alter_sample_dataset_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variantfunctionaldata',
            name='functional_data_tag',
            field=models.TextField(choices=[('Functional Data', (('Biochemical Function', '{"description": "Gene product performs a biochemical function shared with other known genes in the disease of interest, or consistent with the phenotype.", "color": "#311B92"}'), ('Protein Interaction', '{"description": "Gene product interacts with proteins previously implicated (genetically or biochemically) in the disease of interest.", "color": "#4A148C"}'), ('Expression', '{"description": "Gene is expressed in tissues relevant to the disease of interest and/or is altered in expression in patients who have the disease.", "color": "#7C4DFF"}'), ('Patient Cells', '{"description": "Gene and/or gene product function is demonstrably altered in patients carrying candidate mutations.", "color": "#B388FF"}'), ('Non-patient cells', '{"description": "Gene and/or gene product function is demonstrably altered in human cell culture models carrying candidate mutations.", "color": "#9575CD"}'), ('Animal Model', '{"description": "Non-human animal models with a similarly disrupted copy of the affected gene show a phenotype consistent with human disease state.", "color": "#AA00FF"}'), ('Non-human cell culture model', '{"description": "Non-human cell-culture models with a similarly disrupted copy of the affected gene show a phenotype consistent with human disease state.", "color": "#BA68C8"}'), ('Rescue', '{"description": "The cellular phenotype in patient-derived cells or engineered equivalents can be rescued by addition of the wild-type gene product.", "color": "#663399"}'))), ('Functional Scores', (('Genome-wide Linkage', '{"metadata_title": "LOD Score", "description": "Max LOD score used in analysis to restrict where you looked for causal variants; provide best score available, whether it be a cumulative LOD score across multiple families or just the best family\'s LOD score.", "color": "#880E4F"}'), ('Bonferroni corrected p-value', '{"metadata_title": "P-value", "description": "Bonferroni-corrected p-value for gene if association testing/burden testing/etc was used to identify the gene.", "color": "#E91E63"}'), ('Kindreds w/ Overlapping SV & Similar Phenotype', '{"metadata_title": "#", "description": "Number of kindreds (1+) previously reported/in databases as having structural variant overlapping the gene and a similar phenotype.", "color": "#FF5252"}'))), ('Additional Kindreds (Literature, MME)', (('Additional Unrelated Kindreds w/ Causal Variants in Gene', '{"metadata_title": "# additional families", "description": "Number of additional kindreds with causal variants in this gene (Any other kindreds from collaborators, MME, literature etc). Do not count your family in this total.", "color": "#D84315"}'),)), ('Additional Information', (('Incomplete Penetrance', '{"description": "Variant has been shown to be disease-causing (in literature, functional studies, etc.) but one or more individuals in this family with the variant do not present with clinical features of the disorder.", "color": "#E985DC"}'), ('Partial Phenotype Contribution', '{"metadata_title": "HPO Terms", "description": "Variant is believed to be part of the solve, explaining only some of the phenotypes.", "color": "#1F42D9"}'), ('Validated Name', '{"description": "Variant name which differs from the computed name.", "color": "#0E7694", "metadata_title": "Name"}')))]),
        ),
    ]
