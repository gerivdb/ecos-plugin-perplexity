# Traçabilité Versions - Espace Métier Perplexity AI

## Vue d'ensemble
Ce document présente le système de traçabilité et de versioning pour l'espace métier Perplexity AI, couvrant le code, la configuration, les données et les déploiements avec une approche GitOps complète.

## Stratégie de Versioning Global

### Philosophie de Versioning

#### Principes Directeurs
- **Semantic Versioning** : Version sémantique pour tous les composants
- **Git Flow** : Workflow Git standardisé avec branches dédiées
- **Immutabilité** : Artefacts versionnés immutables
- **Traçabilité Complète** : Lien entre code, build et déploiement
- **Rollback Sécurisé** : Capacité de retour à toute version antérieure

#### Schema de Versioning Sémantique
```
MAJOR.MINOR.PATCH[-PRE_RELEASE][+BUILD_METADATA]

Exemples:
- 1.0.0 : Release stable
- 1.1.0-alpha.1 : Pre-release alpha
- 1.1.0-rc.2 : Release candidate
- 1.1.0+build.123 : Build avec métadonnées
```

### Architecture de Versioning

#### Structure Repository Multi-Composants
```
perplexity-metier/
├── VERSION                           # Version globale projet
├── CHANGELOG.md                      # Historique des changements
├── .version-metadata.json            # Métadonnées versioning
├── components/
│   ├── orchestrator/
│   │   ├── VERSION
│   │   ├── CHANGELOG.md
│   │   └── src/
│   ├── python-executor/
│   │   ├── VERSION
│   │   ├── CHANGELOG.md
│   │   └── src/
│   └── api-gateway/
│       ├── VERSION
│       ├── CHANGELOG.md
│       └── src/
├── infrastructure/
│   ├── VERSION
│   ├── terraform/
│   └── kubernetes/
└── migrations/
    ├── schema/
    │   ├── v1.0.0__initial.sql
    │   ├── v1.1.0__add_indexes.sql
    │   └── v1.2.0__new_tables.sql
    └── data/
        ├── v1.0.0__seed_data.sql
        └── v1.1.0__reference_data.sql
```

### Git Workflow et Branching Strategy

#### Git Flow Adapté
```yaml
# Configuration Git Flow
branches:
  main:
    description: "Production ready code"
    protection:
      required_reviews: 2
      dismiss_stale_reviews: true
      require_code_owner_reviews: true
      required_status_checks:
        - ci/build
        - ci/test
        - security/scan
  
  develop:
    description: "Integration branch for features"
    auto_merge_from: ["feature/*", "bugfix/*"]
  
  release/*:
    description: "Release preparation branches"
    pattern: "release/v*.*.*"
    merge_to: ["main", "develop"]
  
  hotfix/*:
    description: "Critical fixes for production"
    pattern: "hotfix/v*.*.*"
    merge_to: ["main", "develop"]
  
  feature/*:
    description: "Feature development branches"
    pattern: "feature/[ticket-id]-description"
    merge_to: ["develop"]

# Hooks Git automatiques
hooks:
  pre_commit:
    - version_check
    - code_format
    - security_scan
  
  pre_push:
    - integration_tests
    - version_validation
  
  post_merge:
    - auto_version_bump
    - changelog_update
```

#### Scripts de Versioning Git
```python
#!/usr/bin/env python3
# scripts/version_manager.py
"""
Gestionnaire de versions centralisé pour le projet
Gère versioning sémantique, changelog et tags Git
"""

import os
import json
import subprocess
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

class VersionType(Enum):
    MAJOR = "major"
    MINOR = "minor" 
    PATCH = "patch"
    PRE_RELEASE = "pre-release"

@dataclass
class VersionMetadata:
    """Métadonnées de version"""
    version: str
    timestamp: str
    commit_hash: str
    branch: str
    author: str
    build_number: Optional[int] = None
    components: Dict[str, str] = None
    
    def __post_init__(self):
        if self.components is None:
            self.components = {}

class VersionManager:
    """Gestionnaire central des versions"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.version_file = self.project_root / "VERSION"
        self.metadata_file = self.project_root / ".version-metadata.json"
        self.changelog_file = self.project_root / "CHANGELOG.md"
        
        # Composants versionnés séparément
        self.components = {
            "orchestrator": self.project_root / "components" / "orchestrator",
            "python-executor": self.project_root / "components" / "python-executor",
            "api-gateway": self.project_root / "components" / "api-gateway",
            "infrastructure": self.project_root / "infrastructure"
        }
    
    def get_current_version(self) -> str:
        """Récupère version actuelle du projet"""
        if self.version_file.exists():
            return self.version_file.read_text().strip()
        return "0.0.0"
    
    def get_component_version(self, component: str) -> str:
        """Récupère version d'un composant spécifique"""
        if component not in self.components:
            raise ValueError(f"Composant {component} inconnu")
        
        component_version_file = self.components[component] / "VERSION"
        if component_version_file.exists():
            return component_version_file.read_text().strip()
        return "0.0.0"
    
    def parse_version(self, version_str: str) -> Tuple[int, int, int, Optional[str], Optional[str]]:
        """Parse version sémantique"""
        # Regex pour version sémantique complète
        pattern = r'^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$'
        
        match = re.match(pattern, version_str)
        if not match:
            raise ValueError(f"Version invalide: {version_str}")
        
        major, minor, patch = map(int, match.groups()[:3])
        pre_release = match.group(4)
        build_meta = match.group(5)
        
        return major, minor, patch, pre_release, build_meta
    
    def format_version(self, major: int, minor: int, patch: int,
                      pre_release: Optional[str] = None,
                      build_meta: Optional[str] = None) -> str:
        """Formate version sémantique"""
        version = f"{major}.{minor}.{patch}"
        
        if pre_release:
            version += f"-{pre_release}"
        if build_meta:
            version += f"+{build_meta}"
        
        return version
    
    def bump_version(self, version_type: VersionType, 
                    pre_release_tag: Optional[str] = None,
                    component: Optional[str] = None) -> str:
        """Incrémente version selon le type"""
        
        if component:
            current_version = self.get_component_version(component)
            version_file = self.components[component] / "VERSION"
        else:
            current_version = self.get_current_version()
            version_file = self.version_file
        
        major, minor, patch, current_pre, _ = self.parse_version(current_version)
        
        # Logique d'incrémentation
        if version_type == VersionType.MAJOR:
            major += 1
            minor = 0
            patch = 0
            pre_release = None
        elif version_type == VersionType.MINOR:
            minor += 1
            patch = 0
            pre_release = None
        elif version_type == VersionType.PATCH:
            patch += 1
            pre_release = None
        elif version_type == VersionType.PRE_RELEASE:
            if pre_release_tag:
                if current_pre and current_pre.startswith(pre_release_tag):
                    # Incrémente numéro pre-release existant
                    parts = current_pre.split('.')
                    if len(parts) >= 2 and parts[1].isdigit():
                        parts[1] = str(int(parts[1]) + 1)
                        pre_release = '.'.join(parts)
                    else:
                        pre_release = f"{pre_release_tag}.1"
                else:
                    pre_release = f"{pre_release_tag}.1"
            else:
                pre_release = current_pre
        
        # Génère build metadata si nécessaire
        build_meta = self._generate_build_metadata()
        
        new_version = self.format_version(major, minor, patch, pre_release, build_meta)
        
        # Sauvegarde nouvelle version
        version_file.write_text(new_version)
        
        print(f"📈 Version {'[' + component + ']' if component else 'globale'}: {current_version} → {new_version}")
        return new_version
    
    def _generate_build_metadata(self) -> str:
        """Génère métadonnées de build"""
        try:
            commit_hash = subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"],
                text=True
            ).strip()
            
            timestamp = datetime.now().strftime("%Y%m%d%H%M")
            
            return f"build.{timestamp}.{commit_hash}"
        except subprocess.CalledProcessError:
            return f"build.{datetime.now().strftime('%Y%m%d%H%M')}"
    
    def get_git_info(self) -> Dict[str, str]:
        """Récupère informations Git actuelles"""
        try:
            return {
                "commit_hash": subprocess.check_output(
                    ["git", "rev-parse", "HEAD"], text=True
                ).strip(),
                "short_hash": subprocess.check_output(
                    ["git", "rev-parse", "--short", "HEAD"], text=True
                ).strip(),
                "branch": subprocess.check_output(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True
                ).strip(),
                "author": subprocess.check_output(
                    ["git", "log", "-1", "--pretty=format:%an <%ae>"], text=True
                ).strip(),
                "timestamp": subprocess.check_output(
                    ["git", "log", "-1", "--pretty=format:%ci"], text=True
                ).strip()
            }
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Erreur Git: {e}")
            return {}
    
    def save_version_metadata(self, version: str) -> None:
        """Sauvegarde métadonnées de version"""
        git_info = self.get_git_info()
        
        # Versions des composants
        component_versions = {}
        for comp_name, comp_path in self.components.items():
            try:
                component_versions[comp_name] = self.get_component_version(comp_name)
            except ValueError:
                component_versions[comp_name] = "0.0.0"
        
        metadata = VersionMetadata(
            version=version,
            timestamp=datetime.now().isoformat(),
            commit_hash=git_info.get("commit_hash", "unknown"),
            branch=git_info.get("branch", "unknown"),
            author=git_info.get("author", "unknown"),
            components=component_versions
        )
        
        # Sauvegarde en JSON
        with open(self.metadata_file, 'w') as f:
            json.dump(asdict(metadata), f, indent=2)
        
        print(f"💾 Métadonnées version sauvegardées: {self.metadata_file}")
    
    def load_version_metadata(self) -> Optional[VersionMetadata]:
        """Charge métadonnées de version"""
        if not self.metadata_file.exists():
            return None
        
        with open(self.metadata_file, 'r') as f:
            data = json.load(f)
        
        return VersionMetadata(**data)
    
    def generate_changelog_entry(self, version: str, component: Optional[str] = None) -> str:
        """Génère entrée changelog depuis commits Git"""
        
        # Détermine range de commits
        try:
            if component:
                # Dernière version du composant
                last_version = self.get_component_version(component)
                tag_pattern = f"{component}-v{last_version}"
            else:
                # Dernière version globale
                last_version = self.get_current_version()
                tag_pattern = f"v{last_version}"
            
            # Tente de trouver le dernier tag
            try:
                subprocess.check_output(
                    ["git", "tag", "-l", tag_pattern],
                    text=True
                ).strip()
                commit_range = f"{tag_pattern}..HEAD"
            except:
                # Pas de tag trouvé, prend tous les commits
                commit_range = "HEAD"
            
            # Récupère commits dans le range
            cmd = ["git", "log", commit_range, "--pretty=format:%H|%s|%an|%ad", "--date=short"]
            
            if component:
                # Filtre par paths du composant
                cmd.extend(["--", str(self.components[component])])
            
            commits_output = subprocess.check_output(cmd, text=True).strip()
            
        except subprocess.CalledProcessError:
            print("⚠️  Erreur récupération commits Git")
            return f"## [{version}] - {datetime.now().strftime('%Y-%m-%d')}\n\nPas de changelog disponible.\n"
        
        if not commits_output:
            return f"## [{version}] - {datetime.now().strftime('%Y-%m-%d')}\n\nAucune modification.\n"
        
        commits = commits_output.split('\n')
        
        # Catégorise les commits selon conventional commits
        features = []
        fixes = []
        breaking = []
        docs = []
        others = []
        
        for commit in commits:
            if '|' not in commit:
                continue
            
            hash_commit, subject, author, date = commit.split('|', 3)
            short_hash = hash_commit[:8]
            
            # Parse conventional commit
            if subject.startswith('feat!:') or 'BREAKING CHANGE' in subject:
                breaking.append(f"- {subject.replace('feat!:', '').strip()} `{short_hash}`")
            elif subject.startswith('feat'):
                features.append(f"- {subject.replace('feat:', '').strip()} `{short_hash}`")
            elif subject.startswith('fix'):
                fixes.append(f"- {subject.replace('fix:', '').strip()} `{short_hash}`")
            elif subject.startswith('docs'):
                docs.append(f"- {subject.replace('docs:', '').strip()} `{short_hash}`")
            else:
                others.append(f"- {subject} `{short_hash}`")
        
        # Construit entrée changelog
        changelog_entry = f"## [{version}] - {datetime.now().strftime('%Y-%m-%d')}\n\n"
        
        if breaking:
            changelog_entry += "### 💥 BREAKING CHANGES\n\n"
            changelog_entry += '\n'.join(breaking) + '\n\n'
        
        if features:
            changelog_entry += "### ✨ Nouvelles Fonctionnalités\n\n"
            changelog_entry += '\n'.join(features) + '\n\n'
        
        if fixes:
            changelog_entry += "### 🐛 Corrections de Bugs\n\n"
            changelog_entry += '\n'.join(fixes) + '\n\n'
        
        if docs:
            changelog_entry += "### 📚 Documentation\n\n"
            changelog_entry += '\n'.join(docs) + '\n\n'
        
        if others:
            changelog_entry += "### 🔧 Autres Modifications\n\n"
            changelog_entry += '\n'.join(others) + '\n\n'
        
        return changelog_entry
    
    def update_changelog(self, version: str, component: Optional[str] = None) -> None:
        """Met à jour le changelog"""
        
        changelog_file = self.changelog_file
        if component:
            changelog_file = self.components[component] / "CHANGELOG.md"
        
        new_entry = self.generate_changelog_entry(version, component)
        
        if changelog_file.exists():
            current_content = changelog_file.read_text()
            
            # Insert nouvelle entrée après header principal
            lines = current_content.split('\n')
            
            # Trouve position d'insertion (après # Changelog ou première ## entry)
            insert_position = 0
            for i, line in enumerate(lines):
                if line.startswith('# Changelog') or line.startswith('# CHANGELOG'):
                    insert_position = i + 1
                    break
                elif line.startswith('## ['):
                    insert_position = i
                    break
            
            # Insère nouvelle entrée
            lines.insert(insert_position, new_entry)
            new_content = '\n'.join(lines)
        else:
            # Crée nouveau changelog
            title = f"# Changelog - {component.title()}" if component else "# Changelog"
            new_content = f"{title}\n\n{new_entry}"
        
        changelog_file.write_text(new_content)
        
        prefix = f"[{component}] " if component else ""
        print(f"📝 {prefix}Changelog mis à jour: {changelog_file}")
    
    def create_git_tag(self, version: str, component: Optional[str] = None) -> None:
        """Crée tag Git pour la version"""
        
        if component:
            tag_name = f"{component}-v{version}"
            message = f"Release {component} v{version}"
        else:
            tag_name = f"v{version}"
            message = f"Release v{version}"
        
        print(f"🏷️  Création tag: {tag_name}")
        
        try:
            # Commit les changements de version si nécessaire
            files_to_commit = [str(self.version_file), str(self.metadata_file)]
            
            if component:
                files_to_commit.extend([
                    str(self.components[component] / "VERSION"),
                    str(self.components[component] / "CHANGELOG.md")
                ])
            else:
                files_to_commit.append(str(self.changelog_file))
            
            subprocess.run(["git", "add"] + files_to_commit, check=True)
            
            commit_message = f"chore: release {tag_name}"
            subprocess.run(["git", "commit", "-m", commit_message], check=True)
            
            # Crée tag annoté
            subprocess.run([
                "git", "tag", "-a", tag_name, "-m", message
            ], check=True)
            
            print(f"✅ Tag {tag_name} créé avec succès")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur création tag: {e}")
            raise
    
    def list_versions(self, component: Optional[str] = None) -> List[str]:
        """Liste toutes les versions disponibles"""
        try:
            if component:
                pattern = f"{component}-v*"
            else:
                pattern = "v*"
            
            tags_output = subprocess.check_output([
                "git", "tag", "-l", pattern, "--sort=-version:refname"
            ], text=True).strip()
            
            if not tags_output:
                return []
            
            tags = tags_output.split('\n')
            
            # Extrait versions depuis tags
            versions = []
            for tag in tags:
                if component:
                    version = tag.replace(f"{component}-v", "")
                else:
                    version = tag.replace("v", "")
                versions.append(version)
            
            return versions
            
        except subprocess.CalledProcessError:
            return []
    
    def get_version_diff(self, version1: str, version2: str, 
                        component: Optional[str] = None) -> Dict[str, List[str]]:
        """Compare deux versions et retourne les différences"""
        
        if component:
            tag1 = f"{component}-v{version1}"
            tag2 = f"{component}-v{version2}"
            path_filter = [str(self.components[component])]
        else:
            tag1 = f"v{version1}"
            tag2 = f"v{version2}"
            path_filter = []
        
        try:
            # Récupère commits entre les versions
            cmd = ["git", "log", f"{tag1}..{tag2}", "--pretty=format:%H|%s|%an", "--reverse"]
            if path_filter:
                cmd.extend(["--"] + path_filter)
            
            commits_output = subprocess.check_output(cmd, text=True).strip()
            
            if not commits_output:
                return {"commits": [], "files": []}
            
            commits = []
            for line in commits_output.split('\n'):
                if '|' in line:
                    hash_commit, subject, author = line.split('|', 2)
                    commits.append({
                        "hash": hash_commit[:8],
                        "subject": subject,
                        "author": author
                    })
            
            # Récupère fichiers modifiés
            files_cmd = ["git", "diff", "--name-only", f"{tag1}..{tag2}"]
            if path_filter:
                files_cmd.extend(["--"] + path_filter)
            
            files_output = subprocess.check_output(files_cmd, text=True).strip()
            files = files_output.split('\n') if files_output else []
            
            return {
                "commits": commits,
                "files": files
            }
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur comparaison versions: {e}")
            return {"commits": [], "files": []}
    
    def release_workflow(self, version_type: VersionType, 
                        component: Optional[str] = None,
                        pre_release_tag: Optional[str] = None) -> str:
        """Workflow complet de release"""
        
        print(f"🚀 Début release {version_type.value}")
        if component:
            print(f"   Composant: {component}")
        
        try:
            # 1. Vérifie état Git propre
            status_output = subprocess.check_output(
                ["git", "status", "--porcelain"], text=True
            ).strip()
            
            if status_output:
                print("⚠️  Repository non propre, commit nécessaire")
                print(status_output)
                return None
            
            # 2. Met à jour depuis remote
            subprocess.run(["git", "pull"], check=True)
            
            # 3. Bump version
            new_version = self.bump_version(version_type, pre_release_tag, component)
            
            # 4. Sauvegarde métadonnées
            if not component:  # Métadonnées globales seulement
                self.save_version_metadata(new_version)
            
            # 5. Met à jour changelog
            self.update_changelog(new_version, component)
            
            # 6. Crée tag Git
            self.create_git_tag(new_version, component)
            
            # 7. Push vers remote
            subprocess.run(["git", "push"], check=True)
            subprocess.run(["git", "push", "--tags"], check=True)
            
            print(f"🎉 Release {new_version} terminée avec succès!")
            return new_version
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur release: {e}")
            raise
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
            raise

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Gestionnaire de versions Perplexity AI")
    
    subparsers = parser.add_subparsers(dest="command", help="Commandes disponibles")
    
    # Commande bump
    bump_parser = subparsers.add_parser("bump", help="Incrémenter version")
    bump_parser.add_argument("type", choices=["major", "minor", "patch", "pre-release"],
                           help="Type d'incrémentation")
    bump_parser.add_argument("--component", "-c", help="Composant à versionner")
    bump_parser.add_argument("--pre-release", help="Tag pre-release (alpha, beta, rc)")
    
    # Commande current
    current_parser = subparsers.add_parser("current", help="Afficher version actuelle")
    current_parser.add_argument("--component", "-c", help="Composant spécifique")
    
    # Commande list
    list_parser = subparsers.add_parser("list", help="Lister versions")
    list_parser.add_argument("--component", "-c", help="Composant spécifique")
    
    # Commande diff
    diff_parser = subparsers.add_parser("diff", help="Comparer versions")
    diff_parser.add_argument("version1", help="Version source")
    diff_parser.add_argument("version2", help="Version cible")
    diff_parser.add_argument("--component", "-c", help="Composant spécifique")
    
    # Commande release
    release_parser = subparsers.add_parser("release", help="Workflow release complet")
    release_parser.add_argument("type", choices=["major", "minor", "patch", "pre-release"],
                              help="Type de release")
    release_parser.add_argument("--component", "-c", help="Composant à releaser")
    release_parser.add_argument("--pre-release", help="Tag pre-release")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    version_manager = VersionManager()
    
    try:
        if args.command == "bump":
            version_type = VersionType(args.type)
            version = version_manager.bump_version(
                version_type, 
                args.pre_release, 
                args.component
            )
            print(f"Nouvelle version: {version}")
        
        elif args.command == "current":
            if args.component:
                version = version_manager.get_component_version(args.component)
                print(f"Version {args.component}: {version}")
            else:
                version = version_manager.get_current_version()
                print(f"Version globale: {version}")
        
        elif args.command == "list":
            versions = version_manager.list_versions(args.component)
            component_name = args.component or "globale"
            print(f"Versions {component_name}:")
            for version in versions:
                print(f"  {version}")
        
        elif args.command == "diff":
            diff = version_manager.get_version_diff(
                args.version1, 
                args.version2, 
                args.component
            )
            print(f"Différences {args.version1} → {args.version2}:")
            print(f"  Commits: {len(diff['commits'])}")
            print(f"  Fichiers: {len(diff['files'])}")
            
            for commit in diff['commits'][:10]:  # Top 10
                print(f"    {commit['hash']} {commit['subject']}")
        
        elif args.command == "release":
            version_type = VersionType(args.type)
            version = version_manager.release_workflow(
                version_type,
                args.component,
                args.pre_release
            )
            if version:
                print(f"Release {version} créée avec succès")
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return 1

if __name__ == "__main__":
    exit(main() or 0)
```

### Traçabilité des Déploiements

#### Registry d'Artefacts avec Métadonnées
```python
#!/usr/bin/env python3
# scripts/artifact_registry.py
"""
Registry d'artefacts avec traçabilité complète
Gère versions Docker, Helm charts, et métadonnées de déploiement
"""

import json
import hashlib
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class ArtifactMetadata:
    """Métadonnées d'un artefact"""
    name: str
    version: str
    type: str  # docker, helm, terraform, etc.
    digest: str  # SHA256 digest
    size_bytes: int
    created_at: str
    source_commit: str
    source_branch: str
    build_number: int
    security_scan: Dict
    dependencies: List[str]
    labels: Dict[str, str]

class ArtifactRegistry:
    """Registry d'artefacts avec métadonnées"""
    
    def __init__(self, registry_url: str, auth_token: str):
        self.registry_url = registry_url
        self.auth_token = auth_token
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {auth_token}',
            'Content-Type': 'application/json'
        })
    
    def publish_artifact(self, artifact_path: Path, metadata: ArtifactMetadata) -> bool:
        """Publie artefact avec métadonnées"""
        
        print(f"📦 Publication artefact: {metadata.name}:{metadata.version}")
        
        try:
            # Calcul digest
            digest = self._calculate_digest(artifact_path)
            metadata.digest = digest
            metadata.size_bytes = artifact_path.stat().st_size
            
            # Upload artefact
            artifact_url = f"{self.registry_url}/artifacts/{metadata.name}/{metadata.version}"
            
            with open(artifact_path, 'rb') as f:
                files = {'artifact': f}
                data = {'metadata': json.dumps(asdict(metadata))}
                
                response = self.session.post(artifact_url, files=files, data=data)
                response.raise_for_status()
            
            print(f"✅ Artefact publié: {digest[:12]}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur publication: {e}")
            return False
    
    def get_artifact_metadata(self, name: str, version: str) -> Optional[ArtifactMetadata]:
        """Récupère métadonnées d'un artefact"""
        
        try:
            url = f"{self.registry_url}/artifacts/{name}/{version}/metadata"
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            return ArtifactMetadata(**data)
            
        except Exception as e:
            print(f"❌ Erreur récupération métadonnées: {e}")
            return None
    
    def list_versions(self, name: str) -> List[str]:
        """Liste versions d'un artefact"""
        
        try:
            url = f"{self.registry_url}/artifacts/{name}/versions"
            response = self.session.get(url)
            response.raise_for_status()
            
            return response.json().get('versions', [])
            
        except Exception as e:
            print(f"❌ Erreur listage versions: {e}")
            return []
    
    def get_deployment_history(self, name: str, environment: str) -> List[Dict]:
        """Récupère historique déploiements"""
        
        try:
            url = f"{self.registry_url}/deployments/{name}/{environment}/history"
            response = self.session.get(url)
            response.raise_for_status()
            
            return response.json().get('deployments', [])
            
        except Exception as e:
            print(f"❌ Erreur historique déploiements: {e}")
            return []
    
    def record_deployment(self, name: str, version: str, environment: str,
                         deployment_metadata: Dict) -> bool:
        """Enregistre déploiement"""
        
        deployment_record = {
            'artifact_name': name,
            'artifact_version': version,
            'environment': environment,
            'deployed_at': datetime.now().isoformat(),
            'metadata': deployment_metadata
        }
        
        try:
            url = f"{self.registry_url}/deployments/{name}/{environment}"
            response = self.session.post(url, json=deployment_record)
            response.raise_for_status()
            
            print(f"✅ Déploiement enregistré: {name}:{version} → {environment}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur enregistrement déploiement: {e}")
            return False
    
    def _calculate_digest(self, file_path: Path) -> str:
        """Calcule digest SHA256 d'un fichier"""
        sha256_hash = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        
        return sha256_hash.hexdigest()
    
    def verify_artifact_integrity(self, name: str, version: str) -> bool:
        """Vérifie intégrité d'un artefact"""
        
        metadata = self.get_artifact_metadata(name, version)
        if not metadata:
            return False
        
        # Recalcule digest et compare
        try:
            artifact_url = f"{self.registry_url}/artifacts/{name}/{version}/download"
            response = self.session.get(artifact_url, stream=True)
            response.raise_for_status()
            
            sha256_hash = hashlib.sha256()
            for chunk in response.iter_content(chunk_size=4096):
                sha256_hash.update(chunk)
            
            calculated_digest = sha256_hash.hexdigest()
            
            if calculated_digest == metadata.digest:
                print(f"✅ Intégrité vérifiée: {name}:{version}")
                return True
            else:
                print(f"❌ Intégrité compromise: {name}:{version}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur vérification intégrité: {e}")
            return False
```

### Dashboard de Traçabilité

#### Interface Web de Traçabilité
```html
<!-- templates/traceability_dashboard.html -->
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Traçabilité - Perplexity AI</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .version-timeline {
            position: relative;
            padding-left: 30px;
        }
        
        .version-timeline::before {
            content: '';
            position: absolute;
            left: 15px;
            top: 0;
            bottom: 0;
            width: 2px;
            background: #dee2e6;
        }
        
        .timeline-item {
            position: relative;
            margin-bottom: 30px;
        }
        
        .timeline-item::before {
            content: '';
            position: absolute;
            left: -23px;
            top: 10px;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background: #007bff;
            border: 3px solid #fff;
            box-shadow: 0 0 0 2px #dee2e6;
        }
        
        .deployment-badge {
            font-size: 0.8em;
            padding: 0.25rem 0.5rem;
        }
        
        .component-card {
            transition: transform 0.2s;
        }
        
        .component-card:hover {
            transform: translateY(-2px);
        }
    </style>
</head>
<body>
    <div class="container-fluid py-4">
        <div class="row">
            <div class="col-12">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h1><i class="fas fa-code-branch"></i> Dashboard Traçabilité</h1>
                    <div class="btn-group" role="group">
                        <button class="btn btn-outline-primary" data-bs-toggle="modal" data-bs-target="#versionModal">
                            <i class="fas fa-plus"></i> Nouvelle Version
                        </button>
                        <button class="btn btn-outline-success" onclick="refreshDashboard()">
                            <i class="fas fa-sync-alt"></i> Actualiser
                        </button>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Vue d'ensemble -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card bg-primary text-white">
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <div>
                                <h3 id="globalVersion">-</h3>
                                <p class="mb-0">Version Globale</p>
                            </div>
                            <i class="fas fa-tag fa-2x opacity-50"></i>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-success text-white">
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <div>
                                <h3 id="deploymentsToday">-</h3>
                                <p class="mb-0">Déploiements Aujourd'hui</p>
                            </div>
                            <i class="fas fa-rocket fa-2x opacity-50"></i>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-info text-white">
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <div>
                                <h3 id="activeEnvironments">-</h3>
                                <p class="mb-0">Environnements Actifs</p>
                            </div>
                            <i class="fas fa-server fa-2x opacity-50"></i>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-warning text-white">
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <div>
                                <h3 id="pendingReleases">-</h3>
                                <p class="mb-0">Releases en Attente</p>
                            </div>
                            <i class="fas fa-clock fa-2x opacity-50"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Composants et Versions -->
        <div class="row">
            <div class="col-lg-8">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-puzzle-piece"></i> Composants et Versions</h5>
                    </div>
                    <div class="card-body">
                        <div class="row" id="componentsGrid">
                            <!-- Généré dynamiquement -->
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-lg-4">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-history"></i> Historique Récent</h5>
                    </div>
                    <div class="card-body">
                        <div class="version-timeline" id="recentHistory">
                            <!-- Généré dynamiquement -->
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Timeline Déploiements -->
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header d-flex justify-content-between">
                        <h5><i class="fas fa-project-diagram"></i> Timeline Déploiements par Environnement</h5>
                        <select class="form-select form-select-sm w-auto" id="environmentFilter">
                            <option value="">Tous les environnements</option>
                            <option value="dev">Développement</option>
                            <option value="staging">Staging</option>
                            <option value="production">Production</option>
                        </select>
                    </div>
                    <div class="card-body">
                        <div id="deploymentTimeline" style="height: 400px;">
                            <!-- Graphique timeline -->
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Matrice de Compatibilité -->
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-table"></i> Matrice de Compatibilité des Versions</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-bordered" id="compatibilityMatrix">
                                <!-- Généré dynamiquement -->
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Modal Nouvelle Version -->
    <div class="modal fade" id="versionModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Nouvelle Version</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="versionForm">
                        <div class="mb-3">
                            <label class="form-label">Composant</label>
                            <select class="form-select" id="componentSelect" required>
                                <option value="">Sélectionnez un composant</option>
                                <option value="global">Version Globale</option>
                                <option value="orchestrator">Orchestrator</option>
                                <option value="python-executor">Python Executor</option>
                                <option value="api-gateway">API Gateway</option>
                                <option value="infrastructure">Infrastructure</option>
                            </select>
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label">Type de Version</label>
                            <select class="form-select" id="versionType" required>
                                <option value="patch">Patch (x.x.X)</option>
                                <option value="minor">Minor (x.X.0)</option>
                                <option value="major">Major (X.0.0)</option>
                                <option value="pre-release">Pre-release</option>
                            </select>
                        </div>
                        
                        <div class="mb-3" id="preReleaseGroup" style="display: none;">
                            <label class="form-label">Tag Pre-release</label>
                            <select class="form-select" id="preReleaseTag">
                                <option value="alpha">Alpha</option>
                                <option value="beta">Beta</option>
                                <option value="rc">Release Candidate</option>
                            </select>
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label">Description (optionnelle)</label>
                            <textarea class="form-control" id="releaseDescription" rows="3"
                                    placeholder="Décrivez les changements de cette version..."></textarea>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Annuler</button>
                    <button type="button" class="btn btn-primary" onclick="createVersion()">Créer Version</button>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script>
        // État global du dashboard
        let dashboardData = {};
        
        // Initialisation
        document.addEventListener('DOMContentLoaded', function() {
            loadDashboardData();
            
            // Gestion modal version
            document.getElementById('versionType').addEventListener('change', function() {
                const preReleaseGroup = document.getElementById('preReleaseGroup');
                if (this.value === 'pre-release') {
                    preReleaseGroup.style.display = 'block';
                } else {
                    preReleaseGroup.style.display = 'none';
                }
            });
            
            // Auto-refresh toutes les 30 secondes
            setInterval(loadDashboardData, 30000);
        });
        
        async function loadDashboardData() {
            try {
                const response = await fetch('/api/traceability/dashboard');
                dashboardData = await response.json();
                
                updateOverview();
                updateComponentsGrid();
                updateRecentHistory();
                updateDeploymentTimeline();
                updateCompatibilityMatrix();
                
            } catch (error) {
                console.error('Erreur chargement données:', error);
            }
        }
        
        function updateOverview() {
            document.getElementById('globalVersion').textContent = dashboardData.globalVersion || '-';
            document.getElementById('deploymentsToday').textContent = dashboardData.deploymentsToday || '0';
            document.getElementById('activeEnvironments').textContent = dashboardData.activeEnvironments || '0';
            document.getElementById('pendingReleases').textContent = dashboardData.pendingReleases || '0';
        }
        
        function updateComponentsGrid() {
            const grid = document.getElementById('componentsGrid');
            grid.innerHTML = '';
            
            if (!dashboardData.components) return;
            
            Object.entries(dashboardData.components).forEach(([name, component]) => {
                const statusClass = component.status === 'healthy' ? 'success' : 
                                  component.status === 'warning' ? 'warning' : 'danger';
                
                const card = `
                    <div class="col-md-6 col-lg-4 mb-3">
                        <div class="card component-card h-100">
                            <div class="card-body">
                                <div class="d-flex justify-content-between align-items-start mb-2">
                                    <h6 class="card-title">${component.displayName}</h6>
                                    <span class="badge bg-${statusClass}">${component.status}</span>
                                </div>
                                <p class="card-text text-muted mb-2">v${component.currentVersion}</p>
                                <div class="row text-center">
                                    <div class="col">
                                        <small class="text-muted">Dev</small><br>
                                        <span class="badge deployment-badge bg-light text-dark">${component.environments.dev}</span>
                                    </div>
                                    <div class="col">
                                        <small class="text-muted">Staging</small><br>
                                        <span class="badge deployment-badge bg-warning">${component.environments.staging}</span>
                                    </div>
                                    <div class="col">
                                        <small class="text-muted">Prod</small><br>
                                        <span class="badge deployment-badge bg-success">${component.environments.production}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                
                grid.innerHTML += card;
            });
        }
        
        function updateRecentHistory() {
            const history = document.getElementById('recentHistory');
            history.innerHTML = '';
            
            if (!dashboardData.recentHistory) return;
            
            dashboardData.recentHistory.forEach(event => {
                const item = `
                    <div class="timeline-item">
                        <div class="card">
                            <div class="card-body py-2">
                                <div class="d-flex justify-content-between">
                                    <strong>${event.type}</strong>
                                    <small class="text-muted">${event.timestamp}</small>
                                </div>
                                <p class="mb-0">${event.description}</p>
                                ${event.version ? `<small class="text-muted">Version: ${event.version}</small>` : ''}
                            </div>
                        </div>
                    </div>
                `;
                
                history.innerHTML += item;
            });
        }
        
        function updateDeploymentTimeline() {
            if (!dashboardData.deploymentTimeline) return;
            
            const traces = [];
            const colors = {
                'dev': '#17a2b8',
                'staging': '#ffc107', 
                'production': '#28a745'
            };
            
            Object.entries(dashboardData.deploymentTimeline).forEach(([env, deployments]) => {
                traces.push({
                    x: deployments.map(d => d.timestamp),
                    y: deployments.map(d => d.component),
                    mode: 'markers+text',
                    name: env.charAt(0).toUpperCase() + env.slice(1),
                    marker: {
                        color: colors[env] || '#6c757d',
                        size: 12
                    },
                    text: deployments.map(d => d.version),
                    textposition: 'middle right',
                    hovertemplate: '<b>%{y}</b><br>Version: %{text}<br>%{x}<extra></extra>'
                });
            });
            
            const layout = {
                title: 'Timeline des Déploiements',
                xaxis: {
                    title: 'Date'
                },
                yaxis: {
                    title: 'Composant'
                },
                height: 400,
                margin: { l: 100, r: 50, t: 50, b: 50 }
            };
            
            Plotly.newPlot('deploymentTimeline', traces, layout);
        }
        
        function updateCompatibilityMatrix() {
            const matrix = document.getElementById('compatibilityMatrix');
            matrix.innerHTML = '';
            
            if (!dashboardData.compatibilityMatrix) return;
            
            // Génère tableau de compatibilité
            let html = '<thead><tr><th>Composant</th>';
            
            // Headers colonnes (environnements)
            const environments = ['dev', 'staging', 'production'];
            environments.forEach(env => {
                html += `<th class="text-center">${env.charAt(0).toUpperCase() + env.slice(1)}</th>`;
            });
            html += '</tr></thead><tbody>';
            
            // Lignes composants
            Object.entries(dashboardData.compatibilityMatrix).forEach(([component, versions]) => {
                html += `<tr><td><strong>${component}</strong></td>`;
                
                environments.forEach(env => {
                    const version = versions[env];
                    const compatible = versions.compatible && versions.compatible[env];
                    const cellClass = compatible ? 'bg-success bg-opacity-25' : 'bg-warning bg-opacity-25';
                    
                    html += `<td class="text-center ${cellClass}">
                        <span class="badge bg-light text-dark">${version}</span>
                        ${compatible ? '<i class="fas fa-check text-success ms-1"></i>' : '<i class="fas fa-exclamation-triangle text-warning ms-1"></i>'}
                    </td>`;
                });
                
                html += '</tr>';
            });
            
            html += '</tbody>';
            matrix.innerHTML = html;
        }
        
        async function createVersion() {
            const form = document.getElementById('versionForm');
            const formData = new FormData(form);
            
            const data = {
                component: document.getElementById('componentSelect').value,
                versionType: document.getElementById('versionType').value,
                preReleaseTag: document.getElementById('preReleaseTag').value,
                description: document.getElementById('releaseDescription').value
            };
            
            try {
                const response = await fetch('/api/traceability/versions', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                if (response.ok) {
                    const result = await response.json();
                    alert(`Version ${result.version} créée avec succès!`);
                    
                    // Ferme modal et recharge données
                    bootstrap.Modal.getInstance(document.getElementById('versionModal')).hide();
                    form.reset();
                    loadDashboardData();
                } else {
                    const error = await response.json();
                    alert(`Erreur: ${error.message}`);
                }
            } catch (error) {
                console.error('Erreur création version:', error);
                alert('Erreur lors de la création de la version');
            }
        }
        
        function refreshDashboard() {
            loadDashboardData();
        }
    </script>
</body>
</html>
```

Ce système de traçabilité offre une visibilité complète sur les versions, déploiements et évolution du code dans l'espace métier Perplexity AI, avec une interface intuitive pour les équipes techniques et métier.