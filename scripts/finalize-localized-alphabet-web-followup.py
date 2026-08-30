from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()

container_path = root / 'src/apps/modern/features/libraries/components/GenresItemsContainer.tsx'
container = container_path.read_text(encoding='utf-8')
old_call = """        includeItemTypes: itemType,\n        alphabet,\n        alphabetNavigationSettings\n    });\n"""
new_call = """        includeItemTypes: itemType,\n        alphabet,\n        alphabetNavigationSettings,\n        enabled: Boolean(systemInfo)\n    });\n"""
if old_call not in container:
    raise SystemExit('Expected useGenres parameter block was not found')
container = container.replace(old_call, new_call)
old_empty_check = """    // No genres at all (no letter filter active) - nothing to pick from\n    if (!isLoading && !genres.length && alphabet == null) {\n"""
new_empty_check = """    if (!systemInfo) {\n        return <Loading />;\n    }\n\n    // No genres at all (no letter filter active) - nothing to pick from\n    if (!isLoading && !genres.length && alphabet == null) {\n"""
if old_empty_check not in container:
    raise SystemExit('Expected genres empty-state block was not found')
container_path.write_text(container.replace(old_empty_check, new_empty_check), encoding='utf-8')

hook_path = root / 'src/apps/modern/features/libraries/hooks/api/useGenres.ts'
hook = hook_path.read_text(encoding='utf-8')
old_interface = """    alphabetNavigationSettings?: AlphabetNavigationSettings;\n    userId?: string;\n}\n"""
new_interface = """    alphabetNavigationSettings?: AlphabetNavigationSettings;\n    enabled?: boolean;\n    userId?: string;\n}\n"""
if old_interface not in hook:
    raise SystemExit('Expected GenresParams block was not found')
hook = hook.replace(old_interface, new_interface)
old_enabled = """        enabled: !!api && !!params.userId && !!params.parentId\n    });\n"""
new_enabled = """        enabled: params.enabled !== false && !!api && !!params.userId && !!params.parentId\n    });\n"""
if old_enabled not in hook:
    raise SystemExit('Expected query enabled expression was not found')
hook_path.write_text(hook.replace(old_enabled, new_enabled), encoding='utf-8')
