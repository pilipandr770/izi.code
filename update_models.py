#!/usr/bin/env python3
"""
Script to update all models with PostgreSQL schema support
"""

import re

def update_models_file():
    with open('app/models.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to find class definitions with __tablename__
    pattern = r'(class \w+\(db\.Model\):\s*"""[^"]*"""\s*__tablename__ = \'[^\']+\')'
    
    def replacement(match):
        return match.group(1) + f'\n    __table_args__ = {{\'schema\': SCHEMA_NAME}} if SCHEMA_NAME != \'public\' else {{}}'
    
    # Replace only if __table_args__ is not already present
    lines = content.split('\n')
    updated_lines = []
    
    for i, line in enumerate(lines):
        updated_lines.append(line)
        
        # If this line contains __tablename__ and next line doesn't contain __table_args__
        if '__tablename__' in line and 'class ' not in line:
            if i + 1 < len(lines) and '__table_args__' not in lines[i + 1]:
                updated_lines.append("    __table_args__ = {'schema': SCHEMA_NAME} if SCHEMA_NAME != 'public' else {}")
    
    with open('app/models.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(updated_lines))
    
    print("Models updated with schema support!")

if __name__ == "__main__":
    update_models_file()
