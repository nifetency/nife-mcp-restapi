#!/usr/bin/env python3
"""
REST Client for REST API MCP Server
Handles HTTP requests with error handling and authentication
"""
import logging
import requests
import time
from typing import Dict, Optional, Any
from urllib.parse import urljoin
import base64

logger = logging.getLogger(__name__)

class RestClient:
    """REST client with authentication and error handling"""
    
    def __init__(
        self,
        base_url: str,
        auth_config: Optional[Dict] = None
    ):
        self.base_url = base_url.rstrip('/')
        self.auth_config = auth_config or {'type': 'none'}
        self.session = requests.Session()
        
        # Configure authentication
        self._configure_auth()
    
    def _configure_auth(self):
        """Configure authentication for the session"""
        auth_type = self.auth_config.get('type', 'none')
        
        if auth_type == 'bearer':
            token = self.auth_config.get('token')
            if token:
                self.session.headers['Authorization'] = f'Bearer {token}'
        
        elif auth_type == 'apikey':
            header = self.auth_config.get('header', 'X-API-Key')
            value = self.auth_config.get('value')
            if value:
                self.session.headers[header] = value
        
        elif auth_type == 'basic':
            username = self.auth_config.get('username')
            password = self.auth_config.get('password')
            if username and password:
                credentials = f"{username}:{password}"
                encoded = base64.b64encode(credentials.encode()).decode()
                self.session.headers['Authorization'] = f'Basic {encoded}'
    
    def execute_request(
        self,
        method: str,
        path: str,
        query_params: Optional[Dict] = None,
        body: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: int = 30
    ) -> Any:
        """
        Execute an HTTP request
        
        Args:
            method: HTTP method (get, post, put, delete, etc.)
            path: API endpoint path
            query_params: Query parameters
            body: Request body (for POST, PUT, PATCH)
            headers: Additional headers
            timeout: Request timeout in seconds
            
        Returns:
            Response data (usually dict or list)
        """
        method = method.lower()
        
        # Build full URL
        if path.startswith('http://') or path.startswith('https://'):
            url = path
        else:
            # Remove leading slash if present
            path = path.lstrip('/')
            url = f"{self.base_url}/{path}"
        
        # Prepare headers
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)
        
        # Add content-type for body requests
        if body and 'Content-Type' not in request_headers:
            request_headers['Content-Type'] = 'application/json'
        
        start_time = time.time()
        
        try:
            logger.info(f"Executing {method.upper()} {url}")
            
            # Execute request
            response = self.session.request(
                method=method,
                url=url,
                params=query_params,
                json=body,
                headers=request_headers,
                timeout=timeout
            )
            
            elapsed_time = time.time() - start_time
            logger.info(f"Request completed in {elapsed_time:.2f}s with status {response.status_code}")
            
            # Handle response
            response.raise_for_status()
            
            # Try to parse JSON
            try:
                return response.json()
            except ValueError:
                # Return text if not JSON
                return {
                    'status': response.status_code,
                    'body': response.text,
                    'headers': dict(response.headers)
                }
            
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout after {timeout}s")
            raise Exception(f"Request timeout after {timeout} seconds")
        
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            raise Exception(f"Connection error: {str(e)}")
        
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            
            # Try to get error details from response
            error_detail = ""
            try:
                error_data = e.response.json()
                error_detail = f" - {error_data}"
            except:
                error_detail = f" - {e.response.text[:200]}"
            
            raise Exception(f"HTTP {e.response.status_code}: {str(e)}{error_detail}")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise Exception(f"Request failed: {str(e)}")
        
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            raise Exception(f"Unexpected error: {str(e)}")
    
    def get(
        self,
        path: str,
        query_params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Any:
        """Execute GET request"""
        return self.execute_request('get', path, query_params=query_params, headers=headers)
    
    def post(
        self,
        path: str,
        body: Optional[Dict] = None,
        query_params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Any:
        """Execute POST request"""
        return self.execute_request('post', path, query_params=query_params, body=body, headers=headers)
    
    def put(
        self,
        path: str,
        body: Optional[Dict] = None,
        query_params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Any:
        """Execute PUT request"""
        return self.execute_request('put', path, query_params=query_params, body=body, headers=headers)
    
    def delete(
        self,
        path: str,
        query_params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Any:
        """Execute DELETE request"""
        return self.execute_request('delete', path, query_params=query_params, headers=headers)
    
    def patch(
        self,
        path: str,
        body: Optional[Dict] = None,
        query_params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Any:
        """Execute PATCH request"""
        return self.execute_request('patch', path, query_params=query_params, body=body, headers=headers)
    
    def head(
        self,
        path: str,
        query_params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Any:
        """Execute HEAD request"""
        return self.execute_request('head', path, query_params=query_params, headers=headers)
    
    def options(
        self,
        path: str,
        query_params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Any:
        """Execute OPTIONS request"""
        return self.execute_request('options', path, query_params=query_params, headers=headers)
