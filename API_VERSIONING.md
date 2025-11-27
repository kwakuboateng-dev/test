# API Versioning Strategy

## Current Version: v1

All API endpoints are prefixed with `/api/v1` for future-proofing and backward compatibility.

## Endpoint Structure

### Versioned Endpoints (All API Routes)
```
/api/v1/auth/login
/api/v1/auth/signup
/api/v1/users/me
/api/v1/matches/nearby
/api/v1/chat/ws/{match_id}
/api/v1/photos/upload
/api/v1/themes/
/api/v1/mood/checkin
... (all other endpoints)
```

### Non-Versioned Endpoints
```
/health          # Health check for monitoring tools
/admin           # Admin panel
/                # Root welcome message
```

## Version Lifecycle

### Current: v1 (1.0.0)
- **Status**: Active
- **Support**: Indefinite
- **Breaking Changes**: None planned

### Future Versions

When introducing breaking changes, we'll create a new version (v2) while maintaining v1:

```python
# Both versions running simultaneously
api_v1 = APIRouter(prefix="/api/v1")  # Existing
api_v2 = APIRouter(prefix="/api/v2")  # New with breaking changes

app.include_router(api_v1)
app.include_router(api_v2)
```

## Deprecation Policy

1. **Announcement**: 6 months before deprecation
2. **Warning Headers**: Add deprecation warnings to responses
3. **Support Period**: Previous version supported for 1 year after new version release
4. **End of Life**: Clear communication and migration guide

## Version Migration Guide

### For Mobile App Developers

When a new API version is released:

1. **Review changelog** for breaking changes
2. **Test against new version** in development
3. **Update base URL** in `api.js`:
   ```javascript
   baseURL: `${API_BASE_URL}/api/v2`
   ```
4. **Deploy gradually** using feature flags or staged rollout

### For Backend Developers

Creating a new version:

1. **Create new router** with version prefix
2. **Copy and modify** endpoints with breaking changes
3. **Maintain v1** for backward compatibility
4. **Document changes** in changelog
5. **Update tests** for both versions

## Breaking vs Non-Breaking Changes

### Non-Breaking (Can be added to v1)
- ✅ New endpoints
- ✅ New optional parameters
- ✅ New response fields
- ✅ Bug fixes
- ✅ Performance improvements

### Breaking (Requires new version)
- ❌ Removing endpoints
- ❌ Removing required parameters
- ❌ Changing response structure
- ❌ Changing authentication method
- ❌ Changing data types

## Client Implementation

### Mobile App (React Native/Expo)

```javascript
// api.js
const API_VERSION = 'v1'; // Can be configured per environment

const api = axios.create({
    baseURL: `${API_BASE_URL}/api/${API_VERSION}`,
    // ...
});
```

### Web App

```javascript
const API_BASE = process.env.REACT_APP_API_URL;
const API_VERSION = process.env.REACT_APP_API_VERSION || 'v1';

fetch(`${API_BASE}/api/${API_VERSION}/users/me`);
```

## Monitoring

Track version usage in logs:

```python
@app.middleware("http")
async def log_api_version(request: Request, call_next):
    # Extract version from path
    if request.url.path.startswith("/api/"):
        version = request.url.path.split("/")[2]  # e.g., "v1"
        logger.info(f"API {version} request: {request.method} {request.url.path}")
    return await call_next(request)
```

## Changelog

### v1.0.0 (Current)
- Initial release with API versioning
- All endpoints under `/api/v1`
- Full feature set including:
  - Authentication
  - User management
  - Matching system
  - Chat/messaging
  - Premium features (themes, mood, quizzes, etc.)

## Future Considerations

### v2 (Planned Features)
- GraphQL support
- Improved pagination
- Enhanced filtering
- Real-time subscriptions
- Batch operations

### v3 (Long-term)
- gRPC support
- Advanced analytics
- AI-powered recommendations

## Support

For questions about API versioning:
- Check this documentation
- Review the changelog
- Contact the development team

## Best Practices

1. **Always specify version** in client code
2. **Don't hardcode URLs** - use environment variables
3. **Test against latest version** regularly
4. **Monitor deprecation warnings**
5. **Plan migrations early**
6. **Use semantic versioning** for your app

## Resources

- [Semantic Versioning](https://semver.org/)
- [API Versioning Best Practices](https://restfulapi.net/versioning/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
