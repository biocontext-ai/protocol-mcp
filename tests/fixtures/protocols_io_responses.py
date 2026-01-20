"""Mock responses for protocols.io API tests."""

SEARCH_RESPONSE = {
    "status_code": 0,
    "items": [
        {
            "id": 12345,
            "title": "RNA Extraction from Tissue Samples",
            "title_html": "RNA Extraction from Tissue Samples",
            "uri": "rna-extraction-from-tissue-samples-abc123",
            "doi": "dx.doi.org/10.17504/protocols.io.abc123",
            "url": "https://www.protocols.io/view/rna-extraction-from-tissue-samples-abc123",
            "stats": {
                "number_of_steps": 15,
                "number_of_views": 1234,
                "number_of_bookmarks": 5,
                "number_of_comments": 2,
            },
            "creator": {
                "name": "Jane Doe",
                "username": "janedoe",
                "affiliation": "Test University",
                "link": None,
                "image": {
                    "source": "https://www.protocols.io/img/avatars/001.png",
                    "placeholder": "https://www.protocols.io/img/avatars/001.png",
                },
            },
            "version_id": 1,
            "public": True,
            "published_on": 1609459200,
            "created_on": 1609459200,
        },
        {
            "id": 12346,
            "title": "High-Quality RNA Isolation Protocol",
            "title_html": "High-Quality RNA Isolation Protocol",
            "uri": "high-quality-rna-isolation-xyz789",
            "doi": "dx.doi.org/10.17504/protocols.io.xyz789",
            "url": "https://www.protocols.io/view/high-quality-rna-isolation-xyz789",
            "stats": {
                "number_of_steps": 22,
                "number_of_views": 567,
                "number_of_bookmarks": 3,
                "number_of_comments": 1,
            },
            "creator": {
                "name": "John Smith",
                "username": "johnsmith",
                "affiliation": "Research Institute",
                "link": None,
                "image": {
                    "source": "https://www.protocols.io/img/avatars/002.png",
                    "placeholder": "https://www.protocols.io/img/avatars/002.png",
                },
            },
            "version_id": 2,
            "public": True,
            "published_on": 1609545600,
            "created_on": 1609545600,
        },
    ],
    "pagination": {
        "current_page": 1,
        "total_pages": 5,
        "total_results": 47,
        "page_size": 10,
        "next_page": "https://www.protocols.io/api/v3/protocols?filter=public&key=RNA&page_id=2&page_size=10",
        "prev_page": None,
        "first": 0,
        "last": 47,
        "changed_on": None,
    },
}

EMPTY_SEARCH_RESPONSE = {
    "status_code": 0,
    "items": [],
    "pagination": {
        "current_page": 1,
        "total_pages": 0,
        "total_results": 0,
        "page_size": 10,
        "next_page": None,
        "prev_page": None,
        "first": 0,
        "last": 0,
        "changed_on": None,
    },
}

PROTOCOL_DETAIL_RESPONSE = {
    "protocol": {
        "id": 12345,
        "title": "RNA Extraction from Tissue Samples",
        "uri": "rna-extraction-from-tissue-samples-abc123",
        "doi": "10.17504/protocols.io.abc123",
        "description": "This protocol describes a reliable method for extracting high-quality RNA from various tissue samples using TRIzol reagent.",
        "before_start": "Ensure all surfaces and equipment are RNase-free. Pre-cool centrifuge to 4°C.",
        "warning": "TRIzol is toxic. Work in a fume hood and wear appropriate PPE.",
        "guidelines": "Keep samples on ice throughout the procedure to prevent RNA degradation.",
        "creator": {
            "name": "Jane Doe",
            "username": "janedoe",
        },
        "version_id": 1,
    }
}

PROTOCOL_STEPS_RESPONSE = {
    "steps": [
        {
            "id": 1,
            "step_number": 1,
            "title": "Sample Preparation",
            "description": "Homogenize 50-100 mg of tissue in 1 mL TRIzol reagent using a tissue homogenizer.",
            "section": "Homogenization",
            "duration": 5,
            "duration_unit": "minutes",
        },
        {
            "id": 2,
            "step_number": 2,
            "title": "Phase Separation",
            "description": "Add 200 µL chloroform per 1 mL TRIzol. Shake vigorously for 15 seconds. Incubate at room temperature for 3 minutes.",
            "section": "Extraction",
            "duration": 3,
            "duration_unit": "minutes",
        },
        {
            "id": 3,
            "step_number": 3,
            "title": "Centrifugation",
            "description": "Centrifuge at 12,000 × g for 15 minutes at 4°C. The mixture separates into three phases.",
            "section": "Extraction",
            "duration": 15,
            "duration_unit": "minutes",
        },
    ]
}

PROTOCOL_MATERIALS_RESPONSE = {
    "materials": [
        {
            "id": 101,
            "name": "TRIzol Reagent",
            "vendor": {"name": "Thermo Fisher Scientific"},
            "catalog_number": "15596026",
            "url": "https://www.thermofisher.com/order/catalog/product/15596026",
        },
        {
            "id": 102,
            "name": "Chloroform",
            "vendor": {"name": "Sigma-Aldrich"},
            "catalog_number": "C2432",
            "url": None,
        },
        {
            "id": 103,
            "name": "Isopropanol",
            "vendor": {"name": "Fisher Scientific"},
            "catalog_number": "A416-4",
            "url": None,
        },
        {
            "id": 104,
            "name": "RNase-free water",
            "vendor": None,
            "catalog_number": None,
            "url": None,
        },
    ]
}
