# Podman Migration Guide

This guide covers the migration from Docker to Podman for the MemoryGraph project.

## 🐳 What is Podman?

Podman is a daemonless container engine that provides a Docker-compatible command-line interface. Key benefits:

- **Rootless containers**: Run containers without root privileges
- **Daemonless**: No background daemon process required
- **Docker-compatible**: Most Docker commands work with Podman
- **Better security**: Enhanced security features and isolation
- **Resource efficiency**: Lower resource overhead

## 📋 Migration Checklist

### ✅ Completed Changes

- [x] Created `podman-compose.yml` and `podman-compose.local.yml` files
- [x] Updated `start.sh` and `stop.sh` scripts to use Podman
- [x] Updated `Makefile` to use Podman commands
- [x] Updated deployment scripts (`deploy.sh`, `setup-ecr.sh`, `setup-graph-services-ecr.sh`)
- [x] Updated setup script (`scripts/setup-local-dev.sh`)
- [x] Updated documentation (`README.md`, `DEVELOPMENT.md`)

### 🔧 Installation Requirements

#### Install Podman

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install podman
```

**CentOS/RHEL/Fedora:**
```bash
sudo dnf install podman
```

**macOS:**
```bash
brew install podman
```

#### Install Podman Compose

```bash
pip install podman-compose
```

#### Verify Installation

```bash
podman --version
podman-compose --version
```

## 🚀 Usage Changes

### Basic Commands

| Docker Command | Podman Command | Notes |
|----------------|----------------|-------|
| `docker build` | `podman build` | Identical syntax |
| `docker run` | `podman run` | Identical syntax |
| `docker-compose up` | `podman-compose up` | Identical syntax |
| `docker ps` | `podman ps` | Identical syntax |
| `docker images` | `podman images` | Identical syntax |

### Starting Services

**Old (Docker):**
```bash
docker-compose up -d
```

**New (Podman):**
```bash
podman-compose -f podman-compose.yml up -d
```

### Building Images

**Old (Docker):**
```bash
docker build -t memorygraph-backend .
```

**New (Podman):**
```bash
podman build -t memorygraph-backend .
```

## 🔧 Configuration Differences

### Volume Handling

Podman handles volumes slightly differently:

- **Named volumes**: Work the same as Docker
- **Bind mounts**: May require different permissions due to rootless operation
- **Volume drivers**: Podman uses different volume drivers

### Networking

Podman uses different networking defaults:

- **Default network**: Uses `podman` instead of `bridge`
- **Port mapping**: Works identically to Docker
- **DNS resolution**: May behave differently in some cases

### Security

Podman provides enhanced security:

- **Rootless containers**: Run without root privileges by default
- **User namespaces**: Better isolation between containers
- **SELinux**: Enhanced SELinux support on RHEL/CentOS systems

## 🐛 Troubleshooting

### Common Issues

#### Permission Denied Errors

If you encounter permission errors with volumes:

```bash
# Check if running rootless
podman info | grep rootless

# If rootless, you may need to adjust volume permissions
sudo chown -R $USER:$USER ./uploads
```

#### Port Already in Use

If ports are already in use:

```bash
# Check what's using the port
sudo netstat -tulpn | grep :8000

# Kill the process or use different ports
```

#### Image Pull Issues

If you have issues pulling images:

```bash
# Login to registries
podman login docker.io
podman login quay.io
```

### Performance Considerations

- **Startup time**: Podman containers may start slightly slower than Docker
- **Memory usage**: Generally lower memory overhead
- **CPU usage**: Similar to Docker in most cases

## 🔄 Rollback Plan

If you need to rollback to Docker:

1. **Revert script changes**:
   ```bash
   git checkout HEAD~1 -- start.sh stop.sh Makefile
   ```

2. **Use original compose files**:
   ```bash
   docker-compose up -d
   ```

3. **Update documentation**:
   - Revert changes to `README.md` and `DEVELOPMENT.md`

## 📚 Additional Resources

- [Podman Documentation](https://docs.podman.io/)
- [Podman Compose Documentation](https://github.com/containers/podman-compose)
- [Docker to Podman Migration Guide](https://podman.io/getting-started/migration)

## 🎯 Next Steps

1. **Test the migration**: Run `./start.sh` to verify everything works
2. **Update team documentation**: Share this guide with your team
3. **Update CI/CD**: Modify GitHub Actions to use Podman if needed
4. **Monitor performance**: Watch for any performance differences
5. **Clean up**: Remove old Docker files if no longer needed

## ⚠️ Important Notes

- **Dockerfiles remain unchanged**: All existing Dockerfiles work with Podman
- **Compose files**: Use `podman-compose.yml` instead of `docker-compose.yml`
- **Scripts**: All scripts now use `podman` and `podman-compose` commands
- **AWS deployment**: ECR integration works the same with Podman
- **Development workflow**: No changes to your daily development workflow
