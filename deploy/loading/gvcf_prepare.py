import hailtop.batch as hb

GATK_CONTAINER = "broadinstitute/gatk:4.1.8.0"


def main(gvcf_path, reference_path, dbsnp_path, output_path: str, **kwargs):

    b = hb.Batch("prepare_gvcf_for_seqr", **kwargs)

    if gvcf_path.endswith(".vcf.gz"):
        gvcf = b.read_input_group(base=gvcf_path, tbi=gvcf_path + ".tbi")
    elif gvcf_path.endswith(".vcf"):
        gvcf = b.read_input_group(base=gvcf_path, idx=gvcf_path + ".idx")
    else:
        raise Exception(f"Unrecognised file extension for gvcf: {gvcf_path}")

    reference = b.read_input_group(
        base=reference_path,
        fai=reference_path + ".fai",
        dict=reference_path.replace(".fasta", "") + ".dict",
    )
    dbsnp = b.read_input_group(base=dbsnp_path, idx=dbsnp_path + ".idx")

    genotype_vcf = submit_gatk_genotype_gvcf(
        b, gvcf=gvcf, reference=reference, dbsnps=dbsnp
    )

    b.write_output(genotype_vcf.out, output_path)

    return b


def submit_gatk_genotype_gvcf(
    b: hb.Batch,
    gvcf,
    reference,
    dbsnps,
    verbosity="INFO",
    interval_padding=25,
    stand_call_confidence=5.0,
):
    j = b.new_job("genotype_gvcf")

    j.image(GATK_CONTAINER)

    output_name = f"{gvcf}.vcf.gz"

    j.command(
        f"""
gatk GenotypeGVCFs \\
  --java-options '-DGATK_STACKTRACE_ON_USER_EXCEPTION=true' \\
  -R {reference.base} \\
  --dbsnp {dbsnps.base} \\
  --allow-old-rms-mapping-quality-annotation-data \\
  --variant {gvcf.base} \\
  --output {output_name} \\
  --verbosity {verbosity} \\
  --create-output-variant-index \\
  --interval-padding {interval_padding} \\
  -stand-call-conf {stand_call_confidence}
"""
    )

    j.command(f"ln {output_name} {j.out}")

    return j


if __name__ == "__main__":
    import os.path

    base = "gs://cpg-fewgenomes-test/kccg/"
    output_path = os.path.join(
        base,
        "mfranklin.HVNTYDSXY_1_170811_FD02523293_Homo-sapiens_ATTACTCG-AGGCTATA_R_170811_CNTROL_KAPADNA_M001.tiny.vcf.gz",
    )
    gvcf_path = os.path.join(
        base,
        "HVNTYDSXY_1_170811_FD02523293_Homo-sapiens_ATTACTCG-AGGCTATA_R_170811_CNTROL_KAPADNA_M001.tiny.g.vcf.gz",
    )

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

    b.run(dry_run=True)
