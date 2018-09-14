import site
import logging
import os
import subprocess
from datetime import datetime

site.addsitedir(r'd:\talha.ahmed\workspace\pyenv_maya\tactic')

import auth.user

# from tactic_client_lib import TacticServerStub
# server = TacticServerStub()

auth.user.login('tactic', 'tactic123', project='suntop_s01')


import app.util as util
logging.basicConfig(
    filename=r'd:\deleting.txt', level=logging.DEBUG, format='%(message)s')

server = util.get_server()
sk = '__search_key__'


def get_sobject_deletables(sobject,
                           versions=2,
                           days=3,
                           keep_current=True,
                           keep_latest=True):
    snaps = server.get_all_children(sobject[sk], 'sthpw/snapshot')
    contexts = {snap['context'] for snap in snaps}
    deletables = []
    for context in contexts:
        csnaps = [
            snap for snap in snaps
            if snap['context'] == context and snap['version'] not in [-1, 0]
        ]
        max_version = max(csnaps, key=lambda s: s['version'])
        for snap in csnaps:
            old_by_version = snap['version'] <= max_version['version'] - versions
            old_by_timestamp = ((datetime.now() - datetime.strptime(
                snap['timestamp'].split('.')[0], '%Y-%m-%d %H:%M:%S')).days >
                                days)
            current_or_latest = ((snap['is_current'] and keep_current)
                                 or (snap['is_latest'] and keep_latest))
            if old_by_version and old_by_timestamp and not current_or_latest:
                paths = [
                    util.translatePath(path)
                    for path in server.get_all_paths_from_snapshot(
                        snap['code'], mode='client_repo')
                ]
                paths = [path for path in paths if os.path.exists(path)]
                deletables.extend(paths)
    return deletables


def unlink(p):
    if os.path.isfile(p):
        try:
            os.unlink(p)
        except WindowsError as wine:
            print str(wine)


def delete_from_assets_in_episodes(versions=2,
                                   days=3,
                                   keep_current=True,
                                   keep_latest=True):
    sobjs = server.eval(
        "@SOBJECT(vfx/asset.vfx/asset_in_episode)"
    )
    for sobj in sobjs:
        print sobj.get('episode_code'), sobj.get('asset_code')
        for p in get_sobject_deletables(
                sobj,
                versions=versions,
                days=days,
                keep_current=keep_current,
                keep_latest=keep_latest):
            unlink(p)
            logging.info(p)
            print p


def delete_from_assets(versions=2, days=3, keep_current=True,
                       keep_latest=True):
    sobjs = server.eval(
        "@SOBJECT(vfx/asset)")
    for sobj in sobjs:
        print sobj.get('code')
        for p in get_sobject_deletables(sobj):
            unlink(p)
            logging.info(p)
            print p


def delete_from_shots(versions=2, days=3, keep_current=True, keep_latest=True):
    subprocess.call(r"net use p: \\nasx\storage\Projects")
    expr = "@SOBJECT(vfx/episode.vfx/sequence.vfx/shot)"
    sobjs = server.eval(expr)
    for sobj in sobjs:
        print sobj.get('code')
        for p in get_sobject_deletables(
                sobj,
                versions=versions,
                days=days,
                keep_current=keep_current,
                keep_latest=keep_latest):
            unlink(p)
            logging.info(p)
            print p


def delete_from_sequences(versions=2,
                          days=3,
                          keep_current=True,
                          keep_latest=True):
    expr = "@SOBJECT(vfx/episode.vfx/sequence)"
    sobjs = server.eval(expr)
    for sobj in sobjs:
        print sobj.get('code')
        for p in get_sobject_deletables(
                sobj,
                versions=versions,
                days=days,
                keep_current=keep_current,
                keep_latest=keep_latest):
            unlink(p)
            logging.info(p)
            print p


if __name__ == "__main__":
    server.set_project('suntop_s01')
    delete_from_assets(versions=2)
    delete_from_assets_in_episodes(
        versions=1, keep_latest=False, keep_current=True)
    delete_from_shots(versions=2)
    delete_from_sequences(versions=2)
