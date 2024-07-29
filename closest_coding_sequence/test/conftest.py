import pytest

@pytest.fixture
def allele_data1():
    return{
        'A*02:07:98': 'ACGTCAGAATAGCAGGATACT...G.CCGTATA',
        'A*02:07:99': "*ACGTCAGAATAGCAGGATACT...G.CCGTATA*" ,
        'A*02:07:100': "*ACGTCAGAATAGCAGGATACT...*.********" ,
        'A*02:07:101': "ACGTCAGAATAGCAGGATACT...*.*********" ,
        'A*02:07:102': "ACGTCAGAATAGCAGGATACT...*.*********" ,
        'A*02:07:103': "*ACGTCAGAATAGCAGGATACT...*.********" ,
        'A*02:07:104': "*ACGTCAGAATAGCAGGATACT...*.********" ,
        'A*02:07:105': "ACGTCAGAATAGCAGGATACT...*.*******" ,
        'A*02:07:106': "*********************...*.*******" ,
        'A*02:07:107': "*********************...*.*******" 
    }

@pytest.fixture
def allele_data2():
    return {
    'A*02:06:08': "**" ,
    'A*02:06:09N': "ACGTCAGAATAGCAGGATACT...G.CCGTATA" ,
    'A*02:06:10': "*ACGTCAGAATAGCAGGATACT...G.CCGTATA*" ,
    'A*02:06:11': "*ACGTCAGAATAGCAGGATACT...G.CCGTATA*" ,
    'A*02:06:12': "*ACGTCAGAATAGCAGGATACT...G.CCGTATA*" ,
    'A*02:06:13': "**ACGTCAGAATAGCAGGATACT...G.CCGTATA" ,
    'A*02:06:14N': "*ACGTCAGAATAGCAGGATACT...G.CCGTATA*" ,
    'A*02:06:15': "**ACGTCAGAATAGCAGGATACT...G.CCGTATA" ,
}

@pytest.fixture
def allele_data3():
    return { 
    'A*01:03:01': "ACGTCAGAATAGCAGGATACT...G.CCGTATA", 
    'A*02:01:01': "*ACGTCAGAATAGCAGGATACT...C.********", 
    'A*02:02:01': "*ACGTCAGAATAGCAGGATACT...C.********", 
    'A*02:03:01': "*ACGTCAGAATAGCAGGATACT...C.********", 
    'A*02:04:01': "*ACGTCAGAATAGCAGGATACT...C.********", 
    'A*02:05:01':"*ACGTCAGAATAGCAGGATACT...C.********",
    'A*02:05:02': "*ACGTCAGAATAGCAGGATACT...C.********", 
    'A*02:05:03':"*ACGTCAGAATAGCAGGATACT...C.********",
    'A*02:05:04': "ACGTCAGAATAGCAGGATACT...C.",
    'A*02:05:05': "*ACGTCAGAATAGCAGGATACT...C.********", 
    'A*02:05:06':"*ACGTCAGAATAGCAGGATACT...C.********" ,
    'A*02:06:01:01': "*ACGTCAGAATAGCAGGATACT...C.********" ,
    'A*02:06:01:02':"ACGTCAGAATAGCAGGATACT...C.*********" ,
    'A*02:06:01:03': "*ACGTCAGAATAGCAGGATACT...C.********" ,
    'A*02:06:02': "*ACGTCAGAATAGCAGGATACT...C.********" ,
    'A*02:06:03': "*ACGTCAGAATAGCAGGATACT...C.********" ,
    'A*02:06:04': "**ACGTCAGAATAGCAGGATACT...C.*******" ,
    'A*02:06:05': "*ACGTCAGAATAGCAGGATACT...C.********" ,
}

@pytest.fixture
def allele_data4():
    return { 
    'A*01:03:01': "*ACGTCAGAATAGCAGGATACT...C.", 
    'A*02:01:01': "*ACGTCAGAATAGCAGGATACT...C.*", 
    'A*02:02:01': "*ACGTCAGAATAGCAGGATACT...C.*", 
    'A*02:03:01': "*ACGTCAGAATAGCAGGATACT...C.*", 
    'A*02:04:01': "*ACGTCAGAATAGCAGGATACT...C.*", 
    'A*02:05:01':"*ACGTCAGAATAGCAGGATACT...C.*",
    'A*02:05:02': "*ACGTCAGAATAGCAGGATACT...C.*", 
    'A*02:05:03':"*ACGTCAGAATAGCAGGATACT...C.*",
    'A*02:05:04': "*ACGTCAGAATAGCAGGATACT...C.",
    'A*02:05:05': "*ACGTCAGAATAGCAGGATACT...C.*", 
    'A*02:05:06':"*ACGTCAGAATAGCAGGATACT...C.*" ,
    'A*02:06:01:01': "*ACGTCAGAATAGCAGGATACT...C.*" ,
    'A*02:06:01:02':"ACGTCAGAATAGCAGGATACT...C.**" ,
    'A*02:06:01:03': "*ACGTCAGAATAGCAGGATACT...C.*" ,
    'A*02:06:02': "*ACGTCAGAATAGCAGGATACT...C.*" ,
    'A*02:06:03': "*ACGTCAGAATAGCAGGATACT...C.*" ,
    'A*02:06:04': "**ACGTCAGAATAGCAGGATACT...C." ,
    'A*02:06:05': "*ACGTCAGAATAGCAGGATACT...C.*" ,
}

@pytest.fixture
def allele_name():
    return ["A*02:07:107", "A*02:07:98", "A*02:06:15", "A*02:06:09N", "A*02:06:05", "A*02:05:03"]

@pytest.fixture
def expected():
    return [{'A*02:07:98': 'ACGTCAGAATAGCAGGATACT...G.CCGTATA'},
    {'A*02:07:98': 'ACGTCAGAATAGCAGGATACT...G.CCGTATA'},
    {'A*02:06:09N': 'ACGTCAGAATAGCAGGATACT...G.CCGTATA'},
    {'A*02:06:09N': 'ACGTCAGAATAGCAGGATACT...G.CCGTATA'},
    {'A*02:05:04': 'ACGTCAGAATAGCAGGATACT...C.'},
    {'A*01:03:01': 'ACGTCAGAATAGCAGGATACT...G.CCGTATA'}
    ]