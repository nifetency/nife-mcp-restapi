#!/usr/bin/env python3
"""
Intelligent Schema Manager for REST APIs
Automatically discovers and generates tools from OpenAPI/Swagger specs
"""
import logging
import requests
import json
import yaml
import os
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class SchemaManager:
    """Manages OpenAPI/Swagger schema parsing and endpoint discovery"""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        auth_config: Optional[Dict] = None
    ):
        self.base_url = base_url or os.getenv('REST_API_BASE_URL')
        self.auth_config = auth_config or {'type': 'none'}
        
        self.schema: Optional[Dict] = None
        self.endpoints_cache: List[Dict] = []
        self.schemas_cache: Dict[str, Dict] = {}
        self.schema_loaded = False
    
    def load_schema(self, spec_url: str) -> bool:
        """Load OpenAPI/Swagger schema from URL or file"""
        try:
            logger.info(f"Loading OpenAPI specification from: {spec_url}")
            
            # Determine if it's a URL or file path
            if spec_url.startswith('http://') or spec_url.startswith('https://'):
                # Load from URL
                response = requests.get(spec_url, timeout=30)
                response.raise_for_status()
                
                # Determine format from content-type or URL
                content_type = response.headers.get('content-type', '')
                
                if 'yaml' in content_type or spec_url.endswith('.yaml') or spec_url.endswith('.yml'):
                    self.schema = yaml.safe_load(response.text)
                else:
                    self.schema = response.json()
            
            else:
                # Load from file
                if not os.path.exists(spec_url):
                    logger.error(f"File not found: {spec_url}")
                    return False
                
                with open(spec_url, 'r', encoding='utf-8') as f:
                    if spec_url.endswith('.yaml') or spec_url.endswith('.yml'):
                        self.schema = yaml.safe_load(f)
                    else:
                        self.schema = json.load(f)
            
            # Validate schema
            if not self._validate_schema():
                return False
            
            # Parse schema
            self._parse_schema()
            
            self.schema_loaded = True
            logger.info(f"✓ OpenAPI schema loaded successfully")
            logger.info(f"  - API Title: {self.get_api_info().get('title', 'Unknown')}")
            logger.info(f"  - API Version: {self.get_api_info().get('version', 'Unknown')}")
            logger.info(f"  - {len(self.endpoints_cache)} endpoints")
            logger.info(f"  - {len(self.schemas_cache)} schemas")
            
            return True
            
        except Exception as e:
            logger.error(f"Schema loading failed: {e}", exc_info=True)
            return False
    
    def _validate_schema(self) -> bool:
        """Validate OpenAPI/Swagger schema"""
        if not self.schema:
            logger.error("Schema is empty")
            return False
        
        # Check for OpenAPI 3.x
        if 'openapi' in self.schema:
            version = self.schema['openapi']
            if not version.startswith('3.'):
                logger.warning(f"OpenAPI version {version} may not be fully supported")
            logger.info(f"Detected OpenAPI {version}")
            return True
        
        # Check for Swagger 2.0
        elif 'swagger' in self.schema:
            version = self.schema['swagger']
            if version != '2.0':
                logger.warning(f"Swagger version {version} may not be fully supported")
            logger.info(f"Detected Swagger {version}")
            return True
        
        else:
            logger.error("Neither OpenAPI nor Swagger version found in schema")
            return False
    
    def _parse_schema(self):
        """Parse OpenAPI/Swagger schema and build caches"""
        # Determine OpenAPI version
        is_openapi3 = 'openapi' in self.schema
        
        # Parse paths/endpoints
        paths = self.schema.get('paths', {})
        
        for path, path_item in paths.items():
            # Get path-level parameters
            path_level_params = path_item.get('parameters', [])
            
            # Process each HTTP method
            for method in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
                if method not in path_item:
                    continue
                
                operation = path_item[method]
                
                # Build endpoint info
                endpoint = {
                    'method': method,
                    'path': path,
                    'description': operation.get('summary', operation.get('description', 'No description')),
                    'operation_id': operation.get('operationId', f"{method}_{path}"),
                    'tags': operation.get('tags', []),
                    'path_params': [],
                    'query_params': [],
                    'request_body': None,
                    'responses': {}
                }
                
                # Parse parameters
                all_params = path_level_params + operation.get('parameters', [])
                
                for param in all_params:
                    # Handle $ref
                    if '$ref' in param:
                        param = self._resolve_ref(param['$ref'])
                    
                    param_info = {
                        'name': param.get('name'),
                        'description': param.get('description', ''),
                        'required': param.get('required', False),
                        'type': self._get_param_type(param, is_openapi3),
                        'default': param.get('default'),
                        'enum': param.get('enum')
                    }
                    
                    param_in = param.get('in', '')
                    
                    if param_in == 'path':
                        endpoint['path_params'].append(param_info)
                    elif param_in == 'query':
                        endpoint['query_params'].append(param_info)
                
                # Parse request body (OpenAPI 3.x)
                if is_openapi3 and 'requestBody' in operation:
                    request_body = operation['requestBody']
                    content = request_body.get('content', {})
                    
                    # Get JSON schema if available
                    json_content = content.get('application/json', {})
                    schema = json_content.get('schema', {})
                    
                    endpoint['request_body'] = {
                        'description': request_body.get('description', ''),
                        'required': request_body.get('required', False),
                        'schema': schema
                    }
                
                # Parse responses
                responses = operation.get('responses', {})
                for status_code, response in responses.items():
                    endpoint['responses'][status_code] = {
                        'description': response.get('description', '')
                    }
                
                self.endpoints_cache.append(endpoint)
        
        # Parse schemas/definitions
        if is_openapi3:
            # OpenAPI 3.x: components.schemas
            components = self.schema.get('components', {})
            schemas = components.get('schemas', {})
        else:
            # Swagger 2.0: definitions
            schemas = self.schema.get('definitions', {})
        
        for schema_name, schema_def in schemas.items():
            self.schemas_cache[schema_name] = schema_def
    
    def _get_param_type(self, param: Dict, is_openapi3: bool) -> str:
        """Extract parameter type"""
        if is_openapi3:
            schema = param.get('schema', {})
            return schema.get('type', 'string')
        else:
            return param.get('type', 'string')
    
    def _resolve_ref(self, ref: str) -> Dict:
        """Resolve $ref reference"""
        # Simple reference resolution
        # Format: #/components/schemas/SchemaName or #/definitions/SchemaName
        parts = ref.split('/')
        
        if len(parts) < 2:
            return {}
        
        # Navigate through schema
        current = self.schema
        for part in parts[1:]:  # Skip the '#'
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return {}
        
        return current if isinstance(current, dict) else {}
    
    def get_all_endpoints(self) -> List[Dict]:
        """Get all available endpoints"""
        return self.endpoints_cache
    
    def get_endpoint_info(self, method: str, path: str) -> Optional[Dict]:
        """Get detailed information about a specific endpoint"""
        method = method.lower()
        
        for endpoint in self.endpoints_cache:
            if endpoint['method'] == method and endpoint['path'] == path:
                return endpoint
        
        return None
    
    def get_all_schemas(self) -> Dict[str, Dict]:
        """Get all schema definitions"""
        return self.schemas_cache
    
    def get_schema_definition(self, schema_name: str) -> Optional[Dict]:
        """Get a specific schema definition"""
        return self.schemas_cache.get(schema_name)
    
    def get_api_info(self) -> Dict[str, str]:
        """Get API information from schema"""
        info = self.schema.get('info', {})
        
        return {
            'title': info.get('title', 'Unknown API'),
            'version': info.get('version', 'Unknown'),
            'description': info.get('description', 'No description'),
            'contact': info.get('contact', {}),
            'license': info.get('license', {})
        }
    
    def search_endpoints(
        self,
        method: Optional[str] = None,
        search_term: Optional[str] = None,
        tag: Optional[str] = None
    ) -> List[Dict]:
        """Search for endpoints"""
        results = self.endpoints_cache
        
        # Filter by method
        if method:
            method = method.lower()
            results = [e for e in results if e['method'] == method]
        
        # Filter by search term
        if search_term:
            search_term = search_term.lower()
            results = [
                e for e in results
                if search_term in e['path'].lower() or
                   search_term in e['description'].lower()
            ]
        
        # Filter by tag
        if tag:
            results = [e for e in results if tag in e.get('tags', [])]
        
        return results
