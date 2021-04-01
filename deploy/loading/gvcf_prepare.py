import hailtop.batch as hb

GATK_CONTAINER = "broadinstitute/gatk:4.1.8.0"


def main(gvcf_path, reference_path, dbsnp_path, output_path: str, **kwargs):

    b = hb.Batch("prepare_gvcf_for_seqr", **kwargs)

    gvcf = b.read_input(gvcf_path)
    reference = b.read_input(reference_path)
    # reference = b.read_input_group(
    #     base=reference_path, dict=reference_path.replace(".fasta", "") + ".dict"
    # )
    dbsnp = b.read_input_group(base=dbsnp_path, idx=dbsnp_path + ".idx")
    dbsnp = b.read_input(dbsnp_path)

    genotype_vcf = submit_gatk_genotype_gvcf(
        b, gvcf=gvcf, reference=reference, dbsnps=dbsnp
    )

    b.write_output(genotype_vcf.out, output_path)

    return b


def submit_gatk_genotype_gvcf(b: hb.Batch, gvcf, reference, dbsnps):
    j = b.new_job("genotype_gvcf")

    j.image(GATK_CONTAINER)

    j.command(
        f"""
gatk GenotypeGVCFs \\
  --java-options '-DGATK_STACKTRACE_ON_USER_EXCEPTION=true' \\
  -R {reference}
  --dbsnp {dbsnps}
  --allow-old-rms-mapping-quality-annotation-data \
  --variant {gvcf}
  --output {j.out}
  --verbosity INFO
  --create-output-variant-index \
  --interval-padding 25 \
  -stand-call-conf 5.0
"""
    )

    return j


if __name__ == "__main__":
    import os.path

    output_path = "gs://cpg-fewgenomes-upload/kccg/mfranklin.HVNTYDSXY_1_170811_FD02523293_Homo-sapiens_ATTACTCG-AGGCTATA_R_170811_CNTROL_KAPADNA_M001.tiny.vcf.gz"
    gvcf_path = "gs://cpg-fewgenomes-upload/kccg/HVNTYDSXY_1_170811_FD02523293_Homo-sapiens_ATTACTCG-AGGCTATA_R_170811_CNTROL_KAPADNA_M001.tiny.g.vcf.gz"

    BROAD_REF_BUCKET = "gs://gcp-public-data--broad-references/hg38/v0"
    reference_path = os.path.join(BROAD_REF_BUCKET, "Homo_sapiens_assembly38.fasta")
    dbsnp_path = os.path.join(BROAD_REF_BUCKET, "Homo_sapiens_assembly38.dbsnp138.vcf")
    backend = hb.ServiceBackend(billing_project="michaelfranklin-trial")

    b = main(
        gvcf_path=gvcf_path,
        reference_path=reference_path,
        dbsnp_path=dbsnp_path,
        output_path=output_path,
        backend=backend,
    )

    b.run()
