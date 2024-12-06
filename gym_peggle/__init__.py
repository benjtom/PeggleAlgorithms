from gymnasium.envs.registration import register

register(
    id="Peggle",
    entry_point="gym_peggle.envs:PeggleEnv",
)
