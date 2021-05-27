/** This file contains sample state to use for tests */

export const PROJECT_GUID = 'R0237_1000_genomes_demo'
export const FAMILY_GUID = 'F011652_1'
export const ANALYSIS_GROUP_GUID = 'AG0000183_test_group'
export const SEARCH_HASH = 'd380ed0fd28c3127d07a64ea2ba907d7'
export const GENE_ID = 'ENSG00000228198'
export const SEARCH = { projectFamilies: [{ projectGuid: PROJECT_GUID, familyGuid: FAMILY_GUID }], search: {} }

export const LOCUS_LIST_GUID = "LL00132_2017_monogenic_ibd_gen"
export const LOCUS_LIST = {
  canEdit: false,
  createdBy: "cjmoran@mgh.harvard.edu",
  createdDate: "2017-11-03T00:01:51.912Z",
  description: "",
  isPublic: true,
  lastModifiedDate: "2018-05-02T00:01:24.013Z",
  locusListGuid: LOCUS_LIST_GUID,
  name: "2017 Monogenic IBD Gene List",
  numEntries: 60,
  parsedItems: { items: [{ geneId: 'ENSG00000164458' }], itemMap: { 'TTN': { geneId: 'ENSG00000164458', symbol: 'TTN' } } }
}

export const STATE = {
  savedSearchesLoading: { isLoading: false },
  searchContextLoading: { isLoading: false },
  multiProjectSearchContextLoading: { isLoading: false },
  searchGeneBreakdownLoading: { isLoading: false },
  locusListLoading: { isLoading: false },
  currentSearchHash: SEARCH_HASH,
  searchesByHash: { [SEARCH_HASH]: SEARCH },
  searchGeneBreakdown: { [SEARCH_HASH]: { [GENE_ID]: { total: 3, families: { [FAMILY_GUID]: 2 } } } },
  savedSearchesByGuid: {},
  familiesByGuid: {
    [FAMILY_GUID]: {
      analysisNotes: 'added note',
      analysisStatus: 'Rcpc',
      analysisSummary: '',
      description: '',
      displayName: '1',
      familyGuid: FAMILY_GUID,
      familyId: '1',
      internalCaseReviewNotes: '',
      internalCaseReviewSummary: '',
      pedigreeImage: '/media/pedigree_images/1_w677Gyf.png',
      projectGuid: PROJECT_GUID,
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
    },
  },
  samplesByGuid: {
    S2310658_wal_mc16200_mc16203: {
      createdDate: "2018-03-30T11:50:40.079Z",
      datasetFilePath: "gs://seqr-datasets/GRCh37/cmg_sankaran_wes/CMG_MYOSEQ.vcf.gz",
      datasetName: null,
      datasetType: "VARIANTS",
      individualGuid: "I021476_na19678",
      loadedDate: "2018-03-13T13:25:21.551Z",
      projectGuid: PROJECT_GUID,
      sampleGuid: "S2310656_wal_mc16200_mc16203",
      sampleId: "WAL_MC16200_MC16203",
      isActive: true,
      sampleType: "WES",
    },
    S2310657_wal_mc16200_mc16203: {
      createdDate: "2018-03-30T11:50:40.079Z",
      datasetFilePath: "gs://seqr-datasets/GRCh37/cmg_sankaran_wes/CMG_MYOSEQ.vcf.gz",
      datasetName: null,
      datasetType: "SV",
      individualGuid: "I021476_na19678",
      loadedDate: "2018-03-13T13:25:21.551Z",
      projectGuid: PROJECT_GUID,
      sampleGuid: "S2310656_wal_mc16200_mc16203",
      sampleId: "WAL_MC16200_MC16203",
      isActive: true,
      sampleType: "WES",
    },
    S2310656_wal_mc16200_mc16203: {
      createdDate: "2018-03-30T11:50:40.079Z",
      datasetFilePath: "gs://seqr-datasets/GRCh37/cmg_sankaran_wes/CMG_MYOSEQ.vcf.gz",
      datasetName: null,
      datasetType: "VARIANTS",
      individualGuid: "I021476_na19678",
      loadedDate: "2018-03-13T13:25:21.551Z",
      projectGuid: PROJECT_GUID,
      sampleGuid: "S2310656_wal_mc16200_mc16203",
      sampleId: "WAL_MC16200_MC16203",
      isActive: false,
      sampleType: "WES",
    },

  },
  analysisGroupsByGuid: {
    [ANALYSIS_GROUP_GUID]: {
      analysisGroupGuid: ANALYSIS_GROUP_GUID,
      createdDate: "2018-08-09T18:53:24.207Z",
      description: "",
      familyGuids: [FAMILY_GUID],
      name: "Test Group",
      projectGuid: PROJECT_GUID,
    },
  },
  locusListsByGuid: { [LOCUS_LIST_GUID]: LOCUS_LIST },
  projectsByGuid: {
    [PROJECT_GUID]: {
      createdDate: '2016-05-16T05:37:08.634Z',
      deprecatedLastAccessedDate: '2017-03-14T15:15:42.580Z',
      description: '',
      isMmeEnabled: true,
      lastModifiedDate: '2017-03-14T17:37:32.712Z',
      mmePrimaryDataOwner: 'PI',
      name: '1000 Genomes Demo',
      projectCategoryGuids: [],
      projectGuid: PROJECT_GUID,
      locusListGuids: [LOCUS_LIST_GUID],
    }
  },
  genesById: { [GENE_ID]: { geneId: GENE_ID, geneSymbol: 'OR2M3' } },
  user: {
    date_joined: '2015-02-19T20:22:50.633Z',
    email: 'test@populationgenomics.org.au',
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
