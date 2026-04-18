# OnyxLog TUI Client — Fases

## Tabla de Seguimiento

| Fase | Estado | Progreso | Archivo |
|------|--------|----------|---------|
| 1 — Project Scaffolding | ✅ Completada | 100% | [phase-1.md](phase-1.md) |
| 2 — Configuration Module | ⏳ Pendiente | 0% | [phase-2.md](phase-2.md) |
| 3 — Pydantic Schemas | ⏳ Pendiente | 0% | [phase-3.md](phase-3.md) |
| 4 — API Client Base | ⏳ Pendiente | 0% | [phase-4.md](phase-4.md) |
| 5 — Local SQLite Database | ⏳ Pendiente | 0% | [phase-5.md](phase-5.md) |
| 6 — Auth API Module | ⏳ Pendiente | 0% | [phase-6.md](phase-6.md) |
| 7 — Login Screen | ⏳ Pendiente | 0% | [phase-7.md](phase-7.md) |
| 8 — App Shell (OnyxLogApp) | ⏳ Pendiente | 0% | [phase-8.md](phase-8.md) |
| 9 — Dashboard Screen | ⏳ Pendiente | 0% | [phase-9.md](phase-9.md) |
| 10 — Applications API | ⏳ Pendiente | 0% | [phase-10.md](phase-10.md) |
| 11 — Applications Screen | ⏳ Pendiente | 0% | [phase-11.md](phase-11.md) |
| 12 — Logs API | ⏳ Pendiente | 0% | [phase-12.md](phase-12.md) |
| 13 — Logs Screen | ⏳ Pendiente | 0% | [phase-13.md](phase-13.md) |
| 14 — Settings + Health Check | ⏳ Pendiente | 0% | [phase-14.md](phase-14.md) |
| 15 — SSE Streaming (Real-time Logs) | ⏳ Pendiente | 0% | [phase-15.md](phase-15.md) |
| 16 — CLI + Final Polish | ⏳ Pendiente | 0% | [phase-16.md](phase-16.md) |

## Leyenda de Estados

- **⏳ Pendiente**: No iniciada
- **🔄 En Progreso**: Implementandose
- **✅ Completada**: Todas las tareas finalizadas
- **⏸️ Pausada**: Bloqueada por dependencia externa

## Dependencias entre Fases

```
F1 → F2 → F3 → F4 → F5 → F6 → F7 → F8 → F9
                                        ↓
                                   F9 → F10 → F11
                                        ↓
                                   F9 → F12 → F13
                                              ↓
                                   F11, F13 → F14 → F15 → F16
```
