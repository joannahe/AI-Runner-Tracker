"""Validate every bundled semantic model, ontology and mapping against pinned Apache Ossie 0.2 schemas."""
import json
from pathlib import Path
import sys

import yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

root = Path(__file__).resolve().parent.parent
schema_dir = root / 'schemas/ossie-0.2.0.dev0'
schemas = {name: json.loads((schema_dir / (name + '.json')).read_text()) for name in ('core', 'ontology', 'mapping')}
registry = Registry()
for name, path in [('core', 'core-spec/ossie-schema.json'), ('ontology', 'ontology/ontology.json'), ('mapping', 'ontology/mapping.json')]:
    resource = Resource.from_contents(schemas[name])
    for base in ('https://raw.githubusercontent.com/apache/ossie/main/', 'https://github.com/apache/ossie/'):
        registry = registry.with_resource(base + path, resource)

files = [
    ('fitness_analysis.yaml', 'core'),
    ('fitness_analysis.starrocks.yaml', 'core'),
    ('fitness_ontology.yaml', 'ontology'),
    ('fitness_ontology.starrocks.yaml', 'ontology'),
    ('subject/semantic_models/duckdb/fitness_analysis.yaml', 'core'),
    ('subject/ontology/fitness.ontology.yaml', 'ontology'),
    ('subject/ontology/fitness.mapping.yaml', 'mapping'),
    ('starrocks_project/subject/semantic_models/starrocks/fitness_analysis.yaml', 'core'),
    ('starrocks_project/subject/ontology/fitness.ontology.yaml', 'ontology'),
    ('starrocks_project/subject/ontology/fitness.mapping.yaml', 'mapping'),
]
failed = False
for relative, kind in files:
    document = yaml.safe_load((root / relative).read_text())
    errors = list(Draft202012Validator(schemas[kind], registry=registry).iter_errors(document))
    print(f'{relative}: {"PASS" if not errors else "FAIL"}')
    for error in errors[:5]:
        print('  ', '/'.join(map(str, error.path)), error.message)
    failed |= bool(errors)
sys.exit(1 if failed else 0)
