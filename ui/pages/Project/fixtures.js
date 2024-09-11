/** This file contains sample state to use for tests */

export const STATE1 = {
  familiesByGuid: {
    F011652_1: {
      analysisNotes: 'added note',
      analysisStatus: 'Rcpc',
      analysisSummary: '',
      description: '',
      displayName: '1',
      familyGuid: 'F011652_1',
      familyId: '1',
      internalCaseReviewNotes: '',
      internalCaseReviewSummary: '',
      pedigreeImage: '/media/pedigree_images/1_w677Gyf.png',
      analysedBy: [],
      individualGuids: [
        'I021476_na19678',
        'I021474_na19679',
        'I021475_na19675',
      ],
    },
  },
  individualsByGuid: {
    I021474_na19679: {
      affected: 'N',
      caseReviewStatus: 'I',
      caseReviewStatusLastModifiedBy: null,
      caseReviewStatusLastModifiedDate: null,
      createdDate: '2016-12-05T10:28:21.303Z',
      displayName: '',
      individualGuid: 'I021474_na19679',
      individualId: 'NA19679',
      lastModifiedDate: '2017-03-14T17:37:34.002Z',
      maternalId: '',
      paternalId: '',
      features: [
        {
          category: 'HP:0001507',
          id: 'HP:0011405',
          label: 'Childhood onset short-limb short stature',
        },
        {
          category: 'HP:0001507',
          id: 'HP:0004325',
          label: 'Decreased body weight',
        },
        {
          category: 'HP:0040064',
          id: 'HP:0009821',
          label: 'Forearm undergrowth',
        },
        {
          category: 'HP:0003011',
          id: 'HP:0001290',
          label: 'Generalized hypotonia',
        },
        {
          category: 'HP:0000707',
          id: 'HP:0001250',
          label: 'Seizures',
        },
        {
          category: 'HP:0000924',
          id: 'HP:0002652',
          label: 'Skeletal dysplasia',
        },
      ],
      sampleGuids: [],
      sex: 'F',
    },
    I021475_na19675: {
      affected: 'A',
      caseReviewStatus: 'I',
      caseReviewStatusLastModifiedBy: null,
      caseReviewStatusLastModifiedDate: null,
      createdDate: '2016-12-05T10:28:21.303Z',
      displayName: '',
      individualGuid: 'I021475_na19675',
      individualId: 'NA19675',
      lastModifiedDate: '2017-03-14T17:37:33.838Z',
      maternalId: 'NA19679',
      paternalId: 'NA19678',
      absentFeatures: [
        {
          category: 'HP:0001626',
          id: 'HP:0001631',
          label: 'Defect in the atrial septum',
        },
      ],
      features: [
        {
          category: 'HP:0003011',
          id: 'HP:0001324',
          label: 'Muscle weakness',
        },
      ],
      rejectedGenes: [
        {
          comments: '15 genes, lab A, 2013, NGS, negative ',
          gene: 'LGMD panel',
        },
      ],
      sampleGuids: [],
      sex: 'M',
    },
    I021476_na19678: {
      affected: 'N',
      caseReviewStatus: 'E',
      caseReviewStatusLastModifiedBy: null,
      caseReviewStatusLastModifiedDate: null,
      createdDate: '2016-12-05T10:28:21.303Z',
      displayName: '',
      individualGuid: 'I021476_na19678',
      individualId: 'NA19678',
      lastModifiedDate: '2017-03-14T17:37:33.676Z',
      maternalId: '',
      paternalId: '',
      death_year: 2008,
      sampleGuids: [],
      sex: 'M',
    },
  },
  samplesByGuid: {},
  mmeSubmissionsByGuid: {},
  project: {
    createdDate: '2016-05-16T05:37:08.634Z',
    deprecatedLastAccessedDate: '2017-03-14T15:15:42.580Z',
    description: '',
    isMmeEnabled: true,
    lastModifiedDate: '2017-03-14T17:37:32.712Z',
    mmePrimaryDataOwner: 'PI',
    name: '1000 Genomes Demo',
    projectCategoryGuids: [],
    projectGuid: 'R0237_1000_genomes_demo',
  },
  user: {
    date_joined: '2015-02-19T20:22:50.633Z',
    email: 'seqr+test@populationgenomics.org.au',
    first_name: '',
    id: 1,
    is_active: true,
    is_superuser: true,
    last_login: '2017-03-14T17:44:53.403Z',
    last_name: '',
    username: 'test',
  },
  familyTableState: {
    familiesFilter: 'ACCEPTED',
    familiesSortOrder: 'FAMILY_NAME',
    familiesSortDirection: -1,
    showDetails: true,
  },
}

export const STATE_WITH_2_FAMILIES = {
  familiesByGuid: {
    F011652_1: {
      familyGuid: 'F011652_1',
      projectGuid: 'R0237_1000_genomes_demo',
      analysedBy: [],
      displayName: '1',
      familyId: '1',
      individualGuids: [
        'I021476_na19678_1',
        'I021474_na19679_1',
        'I021475_na19675_1',
      ],
    },
    F011652_2: {
      familyGuid: 'F011652_2',
      projectGuid: 'R0237_1000_genomes_demo',
      analysedBy: [],
      displayName: '2',
      familyId: '2',
      individualGuids: [
        'I021476_na19678_2',
        'I021474_na19679_2',
        'I021475_na19675_2',
      ],
    },
  },
  familyNotesByGuid: {
    FAN001_F011652_1_A: {
      noteGuid: 'FAN001_F011652_1_A',
      familyGuid: 'F011652_2',
      note: 'A note',
      noteType: 'A',
    },
    FAN002_F011652_1_A: {
      noteGuid: 'FAN002_F011652_1_A',
      familyGuid: 'F011652_2',
      note: 'Another note',
      noteType: 'A',
    },
    FAN003_F011652_1_A: {
      noteGuid: 'FAN003_F011652_1_A',
      familyGuid: 'F011652_2',
      note: 'A matchmaker note',
      noteType: 'M',
    },
  },
  individualsByGuid: {
    I021476_na19678_1: {
      projectGuid: 'R0237_1000_genomes_demo',
      familyGuid: 'F011652_1',
      individualId: 'NA19678',
      displayName: 'NA19678',
      affected: 'N',
      caseReviewStatus: 'A',
      caseReviewStatusLastModifiedBy: null,
      caseReviewStatusLastModifiedDate: '2016-12-05T10:28:00.000Z',
      createdDate: '2016-12-05T10:28:00.000Z',
      sampleGuids: [],
      sex: 'F',
    },
    I021475_na19675_1: {
      projectGuid: 'R0237_1000_genomes_demo',
      familyGuid: 'F011652_1',
      individualId: 'NA19675',
      affected: 'A',
      caseReviewStatus: 'I',
      caseReviewStatusLastModifiedBy: null,
      caseReviewStatusLastModifiedDate: '2016-12-05T10:29:00.000Z',
      createdDate: '2016-12-05T10:29:00.000Z',
      sampleGuids: [],
      sex: 'M',
      birthYear: 2010,
      deathYear: 0,
      onsetAge: 'A',
      expectedInheritance: ['S', 'Z'],
      arIui: true,
      affectedRelatives: false,
      arSurrogacy: false,
      arDonorsperm: null,
      absentFeatures: [
        {
          category: 'HP:0001626',
          id: 'HP:0001631',
          label: 'Defect in the atrial septum',
        },
      ],
      features: [
        {
          category: 'HP:0003011',
          id: 'HP:0001324',
          label: 'Muscle weakness',
        },
      ],
      nonstandardFeatures: [{ id: 'A made up feature' }],
      rejectedGenes: [
        {
          comments: '15 genes, lab A, 2013, NGS, negative ',
          gene: 'LGMD panel',
        },
      ],
      disorders: [10243],
      maternalEthnicity: ['White', 'Asian'],
    },
    I021474_na19679_1: {
      projectGuid: 'R0237_1000_genomes_demo',
      familyGuid: 'F011652_1',
      individualId: 'NA19679',
      displayName: 'NA19679_1',
      affected: 'N',
      caseReviewStatus: 'I',
      caseReviewStatusLastModifiedBy: null,
      caseReviewStatusLastModifiedDate: '2016-12-05T10:30:00.000Z',
      createdDate: '2016-12-05T10:30:00.000Z',
      sampleGuids: [],
      sex: 'M',
    },
    I021476_na19678_2: {
      projectGuid: 'R0237_1000_genomes_demo',
      familyGuid: 'F011652_2',
      individualGuid: 'I021476_na19678_2',
      individualId: 'NA19678',
      displayName: 'NA19678_2',
      affected: 'N',
      caseReviewStatus: 'A',
      caseReviewStatusLastModifiedBy: null,
      caseReviewStatusLastModifiedDate: '2016-12-06T10:28:00.000Z',
      createdDate: '2016-12-06T10:28:00.000Z',
      sampleGuids: ['S2310656_wal_mc16200_mc16203'],
      igvSampleGuids: ['IS2310656_wal_mc16200_mc16203'],
      sex: 'F',
    },
    I021475_na19675_2: {
      projectGuid: 'R0237_1000_genomes_demo',
      familyGuid: 'F011652_2',
      individualId: 'NA19675',
      affected: 'A',
      caseReviewStatus: 'I',
      caseReviewStatusLastModifiedBy: null,
      caseReviewStatusLastModifiedDate: '2016-12-06T10:29:00.000Z',
      createdDate: '2016-12-06T10:29:00.000Z',
      sampleGuids: [],
      sex: 'M',
    },
    I021474_na19679_2: {
      projectGuid: 'R0237_1000_genomes_demo',
      familyGuid: 'F011652_2',
      individualId: 'NA19679',
      affected: 'N',
      caseReviewStatus: 'I',
      caseReviewStatusLastModifiedBy: null,
      caseReviewStatusLastModifiedDate: '2016-12-06T10:30:00.000Z',
      createdDate: '2016-12-06T10:30:00.000Z',
      sampleGuids: [],
      sex: 'M',
    },
  },
  samplesByGuid: {
    S2310656_wal_mc16200_mc16203: {
      createdDate: "2018-03-30T11:50:40.079Z",
      datasetFilePath: "gs://seqr-datasets/GRCh37/cmg_sankaran_wes/CMG_MYOSEQ.vcf.gz",
      datasetName: null,
      datasetType: "SNV_INDEL",
      familyGuid: 'F011652_2',
      individualGuid: "I021476_na19678_2",
      loadedDate: "2018-03-13T13:25:21.551Z",
      projectGuid: "R0237_1000_genomes_demo",
      sampleGuid: "S2310656_wal_mc16200_mc16203",
      sampleId: "WAL_MC16200_MC16203",
      isActive: true,
      sampleType: "WES",
    },
  },
  igvSamplesByGuid: {
    IS2310656_wal_mc16200_mc16203: {
      projectGuid: 'R0237_1000_genomes_demo',
      individualGuid: 'I021476_na19678_2',
      sampleGuid: 'IS2310656_wal_mc16200_mc16203',
      filePath: 'gs://seqr-datasets/GRCh37/cmg_sankaran_wes/CMG_MYOSEQ_MC16203.cram',
    },
  },
  analysisGroupsByGuid: {
    AG0000183_test_group: {
      analysisGroupGuid: "AG0000183_test_group",
      createdDate: "2018-08-09T18:53:24.207Z",
      description: "",
      familyGuids: ["F011652_1"],
      name: "Test Group",
      projectGuid: "R0237_1000_genomes_demo",
    },
  },
  currentProjectGuid: 'R0237_1000_genomes_demo',
  projectsByGuid: {
    R0237_1000_genomes_demo: {
      createdDate: '2016-05-16T05:37:08.634Z',
      deprecatedLastAccessedDate: '2017-03-14T15:15:42.580Z',
      description: '',
      isMmeEnabled: true,
      canEdit: true,
      lastModifiedDate: '2017-03-14T17:37:32.712Z',
      mmePrimaryDataOwner: 'PI',
      mmeContactInstitution: 'Broad',
      mmeContactUrl: 'seqr+test@populationgenomics.org.au',
      name: '1000 Genomes Demo',
      projectCategoryGuids: [],
      projectGuid: 'R0237_1000_genomes_demo',
      workspaceName: 'test-namespace',
      workspaceNamespace: 'test-workspace',
      collaborators: [
        {
          dateJoined: '2019-02-20T18:01:36.677Z',
          displayName: '',
          email: 'seqr+test1@populationgenomics.org.au',
          firstName: '',
          hasEditPermissions: true,
          hasViewPermissions: true,
          id: 1041,
          isAnalyst: false,
          lastLogin: '1970-01-01T00:00:00Z',
          lastName: '',
          username: 'test_user1',
        },
        {
          dateJoined: '2019-02-20T18:01:36.677Z',
          displayName: '',
          email: 'seqr+test2@populationgenomics.org.au',
          firstName: '',
          hasEditPermissions: true,
          hasViewPermissions: true,
          id: 1041,
          isAnalyst: true,
          lastLogin: '1970-01-01T00:00:00Z',
          lastName: '',
          username: 'test_user2',
        },
      ],
    },
  },
  familyTableState: {
    familiesSortOrder: 'FAMILY_NAME',
    familiesSortDirection: -1,
    showDetails: true,
  },
  familyTableFilterState: {
    analysisStatus: ['ACCEPTED'],
  },
  caseReviewTableState: {
    familiesFilter: 'ACCEPTED',
  },
  user: {
    date_joined: '2015-02-19T20:22:50.633Z',
    email: 'seqr+test@populationgenomics.org.au',
    first_name: '',
    id: 1,
    is_active: true,
    is_superuser: true,
    last_login: '2017-03-14T17:44:53.403Z',
    last_name: '',
    username: 'test',
    displayName: 'Test User',
  },
  savedVariantTableState: { hideExcluded: true, recordsPerPage: 1 },
  projectCollaboratorsLoading: {},
  projectSavedVariantsLoading: {},
  familyDetailsLoading: {},
  savedVariantsByGuid: {
    SV0000004_116042722_r0390_1000: {
      alt: "T",
      annotation: {
        cadd_phred: "27.2",
        freqs: { AF: null, exac: 0.0006726888333653661, g1k: 0, gnomad_exomes: 0.00006505916317651364 },
        popCounts: { AC: null, AN: null, exac_hemi: null, exac_hom: null, gnomadExomesAC: null, gnomadGenomesAC: null} ,
        vepAnnotations: [
          {
            aminoAcids: "P/X",
            canonical: "YES",
            cdnaPosition: "897",
            cdsPosition: "859",
            codons: "Ccc/cc",
            consequence: "frameshift_variant",
            hgvsc: "ENST00000456743.1:c.862delC",
            hgvsp: "ENSP00000389625.1:p.Leu288SerfsTer10",
            isChosenTranscript: true,
            transcriptId: "ENST00000456743",
          }
        ],
        vepConsequence: "frameshift_variant",
        vepGroup: "frameshift",
        worstVepAnnotation: {
          aminoAcids: "P/X", hgvsc: "ENST00000456743.1:c.862delC", hgvsp: "ENSP00000389625.1:p.Leu288SerfsTer10",
          lof: "HC", lofFilter: "", lofFlags: "SINGLE_EXON", proteinPosition: "287", symbol: "OR2M3"
        }
      },
      chrom: "22",
      clinvar: { clinsig: "", variantId: null },
      familyGuids: ["F011652_1"],
      functionalDataGuids: [],
      genomeVersion: "37",
      genotypes: {
        I021475_na19675_1: {
          ab: 1,
          ad: "0,74",
          alleles: ["T", "T"],
          cnvs: {LRR_median: null, LRR_sd: null, array: null, caller: null, cn: null, freq: null, size: null},
          dp: "74",
          filter: "pass",
          gq: 99,
          numAlt: 2,
          pl: "358,132,0",
        },
        NA19678: {
          ab: 0,
          ad: "77,0",
          alleles: ["TC", "TC"],
          cnvs: {LRR_median: null, LRR_sd: null, array: null, caller: null, cn: null, freq: null, size: null},
          dp: "77",
          filter: "pass",
          gq: 99,
          numAlt: 0,
          pl: "0,232,3036",
        },
        NA19679: {
          ab: 0,
          ad: "71,0",
          alleles: ["TC", "TC"],
          cnvs: {LRR_median: null, LRR_sd: null, array: null, caller: null, cn: null, freq: null, size: null},
          dp: "71",
          filter: "pass",
          gq: 99,
          numAlt: 0,
          pl: "0,213,1918",
        },
      },
      hgmd: {accession: null, class: null},
      liftedOverChrom: "",
      liftedOverGenomeVersion: "38",
      liftedOverPos: "",
      mainTranscriptId: 'ENST00000456743',
      transcripts: {ENSG00000228198: [{
        aminoAcids: "P/X", hgvsc: "ENST00000456743.1:c.862delC", hgvsp: "ENSP00000389625.1:p.Leu288SerfsTer10", lof: "HC",
        lofFilter: "", lofFlags: "SINGLE_EXON", proteinPosition: "287", symbol: "OR2M3", geneId: 'ENSG00000228198',
        majorConsequence: 'frameshift_variant', transcriptId: 'ENST00000456743'
      }]},
      noteGuids: ['VN0727076_116042722_r0390_1000'],
      origAltAlleles: ["T"],
      pos: 45919065,
      projectGuid: 'R0237_1000_genomes_demo',
      ref: "TTTC",
      tagGuids: ['VT1726942_1248367227_r0390_101'],
      variantId: "22-45919065-TTTC-T",
      variantGuid: "SV0000004_116042722_r0390_1000",
      xpos: 22045919065,
    },
    SV0000002_1248367227_r0390_100: {
      alt: "T",
      annotation: {
        cadd_phred: "27.2",
        freqs: { AF: null, exac: 0.0006726888333653661, g1k: 0, gnomad_exomes: 0.00006505916317651364 },
        popCounts: { AC: null, AN: null, exac_hemi: null, exac_hom: null, gnomadExomesAC: null, gnomadGenomesAC: null} ,
        vepAnnotations: [
          {
            aminoAcids: "P/X",
            canonical: "YES",
            cdnaPosition: "897",
            cdsPosition: "859",
            codons: "Ccc/cc",
            consequence: "frameshift_variant",
            hgvsc: "ENST00000456743.1:c.862delC",
            hgvsp: "ENSP00000389625.1:p.Leu288SerfsTer10",
            isChosenTranscript: true,
            transcriptId: "ENST00000456743",
          }
        ],
        vepConsequence: "frameshift_variant",
        vepGroup: "frameshift",
        worstVepAnnotation: {
          aminoAcids: "P/X", hgvsc: "ENST00000456743.1:c.862delC", hgvsp: "ENSP00000389625.1:p.Leu288SerfsTer10",
          lof: "HC", lofFilter: "", lofFlags: "SINGLE_EXON", proteinPosition: "287", symbol: "OR2M3"
        }
      },
      chrom: "1",
      clinvar: { clinsig: "", variantId: null },
      familyGuids: ["F011652_1"],
      functionalDataGuids: ['FD_248367227_r0390_100_1', 'FD_248367227_r0390_100_2'],
      genes: [
        {
          constraints: {
            lof: { constraint: 0.0671997116609769, rank: 8248, totalGenes: 18225 },
            missense: { constraint: -0.7885573790993861, rank: 15052, totalGenes: 18225 },
          },
          diseaseDbPhenotypes: [],
          diseaseGeneLists: [],
          geneId: "ENSG00000228198",
          symbol: "OR2M3",
        }
      ],
      genomeVersion: "37",
      genotypes: {
        I021475_na19675_1: {
          ab: 1,
          ad: "0,74",
          alleles: ["T", "T"],
          cnvs: {LRR_median: null, LRR_sd: null, array: null, caller: null, cn: null, freq: null, size: null},
          dp: "74",
          filter: "pass",
          gq: 99,
          numAlt: 2,
          pl: "358,132,0",
        },
        NA19678: {
          ab: 0,
          ad: "77,0",
          alleles: ["TC", "TC"],
          cnvs: {LRR_median: null, LRR_sd: null, array: null, caller: null, cn: null, freq: null, size: null},
          dp: "77",
          filter: "pass",
          gq: 99,
          numAlt: 0,
          pl: "0,232,3036",
        },
        NA19679: {
          ab: 0,
          ad: "71,0",
          alleles: ["TC", "TC"],
          cnvs: {LRR_median: null, LRR_sd: null, array: null, caller: null, cn: null, freq: null, size: null},
          dp: "71",
          filter: "pass",
          gq: 99,
          numAlt: 0,
          pl: "0,213,1918",
        },
      },
      hgmd: {accession: null, class: null},
      liftedOverChrom: "",
      liftedOverGenomeVersion: "38",
      liftedOverPos: "",
      noteGuids: [],
      origAltAlleles: ["T"],
      mainTranscriptId: 'ENST00000262738',
      transcripts: {ENSG00000228198: [{transcriptId: 'ENST00000262738',  majorConsequence: 'missense_variant'}]},
      pos: 248367227,
      projectGuid: 'R0237_1000_genomes_demo',
      ref: "TC",
      tagGuids: ["VT1726942_1248367227_r0390_100", "VT1708635_1248367227_r0390_100"],
      variantId: "1-248367227-TC-T",
      variantGuid: "SV0000002_1248367227_r0390_100",
      xpos: 1248367227,
    },
    SV0000002_SV48367227_r0390_100: {
      alt: null,
      chrom: "1",
      familyGuids: ["F011652_1"],
      functionalDataGuids: [],
      genomeVersion: "37",
      geneIds: ['ENSG00000228198', 'ENSG00000164458'],
      genotypes: {
        I021475_na19675_1: {
          cn: 0,
          qs: 57,
          numAlt: -1,
        },
        NA19678: {
          cn: 2,
          numAlt: -1,
        },
        NA19679: {
          cn: 2,
          numAlt: -1,
        },
      },
      liftedOverChrom: "",
      liftedOverGenomeVersion: "38",
      liftedOverPos: "",
      noteGuids: [],
      projectGuid: 'R0237_1000_genomes_demo',
      pos: 248367227,
      end: 248369100,
      populations: {
        sv_callset: { af: 0.03, ac: 7, an: 1032 },
        g1k: {},
        exac: {},
        gnomad_genomes: {},
        gnomad_exomes: {},
        topmed: {},
      },
      predictions: { strvctvre: '0.272' },
      ref: null,
      tagGuids: [],
      transcripts: {
        ENSG00000164458: [
          {
            transcriptId: "ENST00000456744",
          }
        ],
        ENSG00000228198: [
          {
            transcriptId: "ENST00000456743",
          }
        ],
      },
      variantId: "batch_123_DEL",
      variantGuid: "SV0000002_SV48367227_r0390_100",
      xpos: 1248367227,
    },
    SV0000003_2246859832_r0390_100: {
      alt: "T",
      annotation: {
        cadd_phred: "27.2",
        freqs: { AF: null, exac: 0.0006726888333653661, g1k: 0, gnomad_exomes: 0.00006505916317651364 },
        popCounts: { AC: null, AN: null, exac_hemi: null, exac_hom: null, gnomadExomesAC: null, gnomadGenomesAC: null} ,
        vepAnnotations: [
          {
            aminoAcids: "P/X",
            canonical: "YES",
            cdnaPosition: "897",
            cdsPosition: "859",
            codons: "Ccc/cc",
            consequence: "frameshift_variant",
            hgvsc: "ENST00000456743.1:c.862delC",
            hgvsp: "ENSP00000389625.1:p.Leu288SerfsTer10",
            isChosenTranscript: true,
            transcriptId: "ENST00000456743",
          }
        ],
        vepConsequence: "frameshift_variant",
        vepGroup: "frameshift",
        worstVepAnnotation: {
          aminoAcids: "P/X", hgvsc: "ENST00000456743.1:c.862delC", hgvsp: "ENSP00000389625.1:p.Leu288SerfsTer10",
          lof: "HC", lofFilter: "", lofFlags: "SINGLE_EXON", proteinPosition: "287", symbol: "OR2M3"
        }
      },
      chrom: "22",
      clinvar: { clinsig: "", variantId: null },
      familyGuids: ["F011652_2"],
      functionalDataGuids: [],
      genes: [
        {
          constraints: {
            lof: { constraint: 0.0671997116609769, rank: 8248, totalGenes: 18225 },
            missense: { constraint: -0.7885573790993861, rank: 15052, totalGenes: 18225 },
          },
          diseaseDbPhenotypes: [],
          diseaseGeneLists: [],
          geneId: "ENSG00000228198",
          symbol: "OR2M3",
        }
      ],
      genomeVersion: "37",
      genotypes: {
        I021475_na19675_1: {
          ab: 1,
          ad: "0,74",
          alleles: ["T", "T"],
          cnvs: {LRR_median: null, LRR_sd: null, array: null, caller: null, cn: null, freq: null, size: null},
          dp: "74",
          filter: "pass",
          gq: 99,
          numAlt: 2,
          pl: "358,132,0",
        },
        NA19678: {
          ab: 0,
          ad: "77,0",
          alleles: ["TC", "TC"],
          cnvs: {LRR_median: null, LRR_sd: null, array: null, caller: null, cn: null, freq: null, size: null},
          dp: "77",
          filter: "pass",
          gq: 99,
          numAlt: 0,
          pl: "0,232,3036",
        },
        NA19679: {
          ab: 0,
          ad: "71,0",
          alleles: ["TC", "TC"],
          cnvs: {LRR_median: null, LRR_sd: null, array: null, caller: null, cn: null, freq: null, size: null},
          dp: "71",
          filter: "pass",
          gq: 99,
          numAlt: 0,
          pl: "0,213,1918",
        },
      },
      hgmd: {accession: null, class: null},
      liftedOverChrom: "",
      liftedOverGenomeVersion: "38",
      liftedOverPos: "",
      mainTranscriptId: null,
      transcripts: {},
      noteGuids: [],
      origAltAlleles: ["T"],
      pos: 248367227,
      projectGuid: 'R0237_1000_genomes_demo',
      ref: "C",
      tagGuids: ['VT1726942_1248367227_r0390_102'],
      variantId: "22-248367227-C-T",
      variantGuid: "SV0000003_2246859832_r0390_100",
      xpos: 22046859832,
    },
    SV0000005_2246859833_r0390_100: {
      alt: "T",
      annotation: {
        cadd_phred: "27.2",
        freqs: { AF: null, exac: 0.0006726888333653661, g1k: 0, gnomad_exomes: 0.00006505916317651364 },
        popCounts: { AC: null, AN: null, exac_hemi: null, exac_hom: null, gnomadExomesAC: null, gnomadGenomesAC: null} ,
        vepAnnotations: [
          {
            aminoAcids: "P/X",
            canonical: "YES",
            cdnaPosition: "897",
            cdsPosition: "859",
            codons: "Ccc/cc",
            consequence: "frameshift_variant",
            hgvsc: "ENST00000456743.1:c.862delC",
            hgvsp: "ENSP00000389625.1:p.Leu288SerfsTer10",
            isChosenTranscript: true,
            transcriptId: "ENST00000456743",
          }
        ],
        vepConsequence: "frameshift_variant",
        vepGroup: "frameshift",
        worstVepAnnotation: {
          aminoAcids: "P/X", hgvsc: "ENST00000456743.1:c.862delC", hgvsp: "ENSP00000389625.1:p.Leu288SerfsTer10",
          lof: "HC", lofFilter: "", lofFlags: "SINGLE_EXON", proteinPosition: "287", symbol: "OR2M3"
        }
      },
      chrom: "22",
      clinvar: { clinsig: "", variantId: null },
      familyGuids: ["F011652_2"],
      functionalDataGuids: [],
      genes: [
        {
          constraints: {
            lof: { constraint: 0.0671997116609769, rank: 8248, totalGenes: 18225 },
            missense: { constraint: -0.7885573790993861, rank: 15052, totalGenes: 18225 },
          },
          diseaseDbPhenotypes: [],
          diseaseGeneLists: [],
          geneId: "ENSG00000228198",
          symbol: "OR2M3",
        }
      ],
      genomeVersion: "37",
      genotypes: {
        I021475_na19675_1: {
          ab: 1,
          ad: "0,74",
          alleles: ["T", "T"],
          cnvs: {LRR_median: null, LRR_sd: null, array: null, caller: null, cn: null, freq: null, size: null},
          dp: "74",
          filter: "pass",
          gq: 99,
          numAlt: 2,
          pl: "358,132,0",
        },
        NA19678: {
          ab: 0,
          ad: "77,0",
          alleles: ["TC", "TC"],
          cnvs: {LRR_median: null, LRR_sd: null, array: null, caller: null, cn: null, freq: null, size: null},
          dp: "77",
          filter: "pass",
          gq: 99,
          numAlt: 0,
          pl: "0,232,3036",
        },
        NA19679: {
          ab: 0,
          ad: "71,0",
          alleles: ["TC", "TC"],
          cnvs: {LRR_median: null, LRR_sd: null, array: null, caller: null, cn: null, freq: null, size: null},
          dp: "71",
          filter: "pass",
          gq: 99,
          numAlt: 0,
          pl: "0,213,1918",
        },
      },
      hgmd: {accession: null, class: null},
      liftedOverChrom: "",
      liftedOverGenomeVersion: "38",
      liftedOverPos: "",
      mainTranscriptId: null,
      transcripts: {},
      noteGuids: [],
      origAltAlleles: ["T"],
      pos: 248367228,
      projectGuid: 'R0237_1000_genomes_demo',
      ref: "C",
      tagGuids: ['VT1726942_1248367227_r0390_102'],
      variantId: "22-248367228-C-T",
      variantGuid: "SV0000005_2246859833_r0390_100",
      xpos: 22046859833,
    },
  },
  variantTagsByGuid: {
    VT1726942_1248367227_r0390_101: {
      category: "Collaboration", color: "#668FE3", dateSaved: "2018-05-25T21:00:51.260Z", name: "Review",
      tagGuid: "VT1726942_1248367227_r0390_101", user: "hsnow@broadinstitute.org",
      variantGuids: ['SV0000004_116042722_r0390_1000']
    },
    VT1726942_1248367227_r0390_100:{
      category: "Collaboration", color: "#668FE3", dateSaved: "2018-05-25T21:00:51.260Z", name: "Review",
      tagGuid: "VT1726942_1248367227_r0390_100", user: "hsnow@broadinstitute.org",
      variantGuids: ['SV0000002_1248367227_r0390_100'],
    },
    VT1708635_1248367227_r0390_100: {
      category: "CMG Discovery Tags",
      color: "#44AA60",
      dateSaved: "2018-03-23T19:59:12.262Z",
      name: "Tier 1 - Phenotype not delineated",
      searchHash: "c2edbeae",
      tagGuid: "VT1708635_1248367227_r0390_100",
      user: "hsnow@broadinstitute.org",
      variantGuids: ['SV0000002_1248367227_r0390_100'],
    },
    VT1726942_1248367227_r0390_102: {
      category: "Collaboration", color: "#668FE3", dateSaved: "2018-05-25T21:00:51.260Z", name: "Excluded",
      tagGuid: "VT1726942_1248367227_r0390_102", user: "hsnow@broadinstitute.org",
      variantGuids: ['SV0000003_2246859832_r0390_100', 'SV0000005_2246859833_r0390_100'],
    }
  },
  variantNotesByGuid: {VN0727076_116042722_r0390_1000: {
    dateSaved: "2018-05-29T17:25:23.770Z", note: "test note edited", noteGuid: "VN0727076_116042722_r0390_1000",
    submitToClinvar: true, user: "hsnow@broadinstitute.org", variantGuids: ['SV0000004_116042722_r0390_1000'],
  }},
  variantFunctionalDataByGuid: {
    FD_248367227_r0390_100_1: { color: "#311B92", dateSaved: "2018-05-24T15:30:04.483Z", metadata: "An updated note",
      metadataTitle: null, name: "Biochemical Function", user: "hsnow@broadinstitute.org",
      tagGuid: 'FD_248367227_r0390_100_1', variantGuids: ['SV0000002_1248367227_r0390_100'], },
    FD_248367227_r0390_100_2: { color: "#880E4F", dateSaved: "2018-05-24T15:34:01.365Z", metadata: "2",
      metadataTitle: "LOD Score", name: "Genome-wide Linkage", user: "hsnow@broadinstitute.org",
      tagGuid: 'FD_248367227_r0390_100_2', variantGuids: ['SV0000002_1248367227_r0390_100'] },
  },
  mmeSubmissionsByGuid: {
    MS021475_na19675_1: {
      submissionGuid: 'MS021475_na19675_1',
      individualGuid: 'I021475_na19675_1',
      createdDate: '2018-05-09T10:29:00.000Z',
      submissionId: 'NA19675_1',
      contactHref: 'mailto:matchmaker@populationgenomics.org.au,test@test.com',
      phenotypes: [
        {id: 'HP:0011405', label: 'Childhood onset short-limb short stature', observed: 'yes'},
        {id: "HP:0012638", label: "Abnormality of nervous system physiology", observed: "no"},
        {id: "HP:0001371", label: "Flexion contracture", observed: "yes"}
      ],
      geneVariants: [
        { geneId: "ENSG00000228198", variantGuid: 'SV0000004_116042722_r0390_1000' },
        { geneId: "ENSG00000228198", variantGuid: 'SV0000002_SV48367227_r0390_100' },
      ],
    }
  },
  mmeResultsByGuid: {
    MR0005038_HK018_0047: {
      submissionGuid: 'MS021475_na19675_1',
      geneVariants: [{geneId: "ENSG00000228198"}],
      phenotypes: [
        {id: "HP:0012638", label: "Abnormality of nervous system physiology", observed: "yes"},
        {id: "HP:0001371", label: "Flexion contracture", observed: "yes"}
      ],
      id: "12531",
      matchStatus: {
        comments: "This seems promising",
        createdDate: "2017-07-18T20:38:53.195Z",
        deemedIrrelevant: false,
        flagForAnalysis: false,
        hostContacted: true,
        matchmakerResultGuid: "MR0005038_HK018_0047",
      },
      patient: {
        contact: { href: "mailto:crowley@unc.edu", institution: "UNC Chapel Hill", name: "James Crowley" },
        id: "12531",
        label: "Childhood Psychiatric Disorder Candidate Genes",
        inheritanceMode: 'Recessive',
      },
      score: 1,
    },

    MR0004688_RGP_105_3: {
      geneVariants: [{ geneId: "ENSG00000272333" }],
      id: "10509",
      submissionGuid: "MS021475_na19675_1",
      matchStatus: {
          comments: "",
          createdDate: "2018-07-26T17:36:25.422Z",
          deemedIrrelevant: false,
          flagForAnalysis: false,
          hostContacted: false,
          matchRemoved: true,
          matchmakerResultGuid: "MR0004688_RGP_105_3",
          weContacted: true
      },
      patient: {
          contact: {
              href: "mailto:j.weiss@vumc.nl",
              institution: "VU University Medical Center",
              name: "Janneke Weiss"
          },
          genomicFeatures: [{ gene: { id: "ENSG00000272333" } }],
          id: "10509",
          label: "2016-174",
          sex: "MALE",
          species: "NCBITaxon:9606"
      },
      phenotypes: [],
      score: 1.0
    },
  },
  search: { familiesByGuid: { result: ['F011652_1', 'F011652_2'] } },
  genesById: { 'ENSG00000228198': { geneId: 'ENSG00000228198', geneSymbol: 'OR2M3' } },
  igvReadsVisibility: {},
  userOptionsByUsername: {
    '3v9tbN78K6': {
      displayName: '',
      email: 'jperezde@broadinstitute.org',
      firstName: '',
      isAnalyst: true,
      lastName: '',
      username: '3v9tbN78K6',
    },
    '4MW8vPtmHG': {
      displayName: 'Mekdes',
      email: 'mgetaneh@broadinstitute.org',
      firstName: 'Mekdes',
      isAnalyst: true,
      lastLogin: '2018-06-11T17:42:45.601Z',
      lastName: '',
      username: '4MW8vPtmHG',
    },
    '5P4YVq2xNj': {
      displayName: '',
      email: 'mwilson@broadinstitute.org',
      firstName: '',
      isAnalyst: true,
      lastName: '',
      username: '5P4YVq2xNj',
    },
    '5jRbtjU9Dz': {
      displayName: 'Alysia Lovgren',
      email: 'alovgren@broadinstitute.org',
      firstName: 'Alysia',
      isAnalyst: false,
      lastName: 'Lovgren',
      username: '5jRbtjU9Dz',
    },
    'test': {
      displayName: '',
      email: 'seqr+test@populationgenomics.org.au',
      firName: '',
      isAnalyst: true,
      last_name: '',
      username: 'test',
    },
    'test_user1': {
      displayName: '',
      email: 'seqr+test1@populationgenomics.org.au',
      firstName: '',
      isAnalyst: false,
      lastName: '',
      username: 'test_user1',
    },
    'test_user2': {
      displayName: '',
      email: 'seqr+test2@populationgenomics.org.au',
      firstName: '',
      isAnalyst: true,
      lastName: '',
      username: 'test_user2',
    },
  },
  rnaSeqDataByIndividual: {
    I021476_na19678_1: {
      outliers: {
        ENSG00000228198: [{ isSignificant: true, pValue: 0.0004 }],
        ENSG00000164458: [{ isSignificant: true, pValue: 0.0073 }],
      },
    },
    I021474_na19679_1: {
      outliers: {
        ENSG00000228198: [{ isSignificant: true, pValue: 0.01 }],
        ENSG00000164458: [{ isSignificant: false, pValue: 0.73 }],
      },
    },
    I021476_na19678_2: { outliers: { ENSG00000228198: [{ isSignificant: true, pValue: 0.0214 }] } },
  },
  phenotypeGeneScoresByIndividual: {
    I021476_na19678_1: {
      ENSG00000228198: {
        lirical: [{
          diseaseId: 'OMIM:618460',
          diseaseName: 'Khan-Khan-Katsanis syndrome',
          rank: 1,
          scores: { compositeLR: 0.066, post_test_probability: 0 },
        }],
      },
    },
  },
}

export const DATA_MANAGER_USER = {
  date_joined: '2015-02-19T20:22:50.633Z',
  email: 'test@broadinstitute.org',
  first_name: '',
  id: 1,
  isActive: true,
  isDataManager: true,
  last_login: '2017-03-14T17:44:53.403Z',
  last_name: '',
  username: 'test',
}
