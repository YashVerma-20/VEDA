# 07. KNOWN LIMITATIONS

## Implementation Boundaries
1. **Live Telemetry**: The system currently does NOT ingest real-time physical vehicle sensor streams over WebSockets/MQTT. It strictly uses dataset-derived JSON fixtures via HTTP POST.
2. **Authentication**: The system lacks OAuth/JWT authentication or Role-Based Access Control (RBAC). It is built as a single-tenant demonstration.
3. **Database**: There is no persistent SQL/NoSQL database. Fleet states are ephemeral per HTTP request.
4. **Scalability**: The Uvicorn backend server relies on asynchronous routing but currently lacks an ASGI multi-worker proxy (e.g., Gunicorn) required for heavy, horizontal production deployment.
5. **3D Assets**: The frontend leverages CSS/SVG abstract representations rather than loading authentic 3D vehicle `.gltf`/`.obj` models due to project constraints.
