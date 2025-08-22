"""Simple test runner for ML mapper validator."""
import sys
from services.ml_mapper import MLMapperValidator
import json


def main(path):
    v = MLMapperValidator(path)
    report = v.validate()
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python test_ml_mapper.py <path-to-ml-template.xlsx>')
        sys.exit(2)
    main(sys.argv[1])
