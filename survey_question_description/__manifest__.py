# Copyright 2020 Jesus Ramoneda <jesus.ramoneda@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Survey Question Description",
    "summary": "Survey Question Description",
    "version": "13.0.1.0.0",
    "category": "Survey",
    "website": "https://www.qubiq.es",
    "author": "QubiQ",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": ["survey"],
    "data": [
        "views/survey_question.xml",
    ],
}
