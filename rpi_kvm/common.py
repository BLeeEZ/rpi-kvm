import asyncio

class System(object):
    @staticmethod
    async def exec_cmd(cmd):
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        return (proc.returncode, stdout, stderr)