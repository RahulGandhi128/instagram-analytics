#!/usr/bin/env python3
"""
Debug route registration - Check what routes are available
"""
from flask import Flask
from api.routes import register_blueprints

app = Flask(__name__)
register_blueprints(app)

print("🔍 Registered Routes:")
print("=" * 50)

for rule in app.url_map.iter_rules():
    print(f"{rule.methods} {rule.rule} -> {rule.endpoint}")

print("\n🎯 Star API Routes:")
print("=" * 30)

star_routes = [rule for rule in app.url_map.iter_rules() if 'star-api' in rule.rule]
for route in star_routes:
    print(f"{list(route.methods)} {route.rule}")

print(f"\n📊 Total routes: {len(list(app.url_map.iter_rules()))}")
print(f"📊 Star API routes: {len(star_routes)}")
