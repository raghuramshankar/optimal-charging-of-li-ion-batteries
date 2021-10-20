import jax.numpy as jnp
import timeit
from jax import grad, jit, vmap
from jax import random

size = 5000
key = random.PRNGKey(0)
x = random.normal(key, (size, size), dtype=jnp.float32)
# print(x)

def multi(x):
    return jnp.dot(x, x.T)  # runs on the GPU

multi_jit = jit(multi)

def run():
    # y = multi_jit(x).block_until_ready()
    y = multi(x).block_until_ready()
    # print(y)

t = timeit.timeit(stmt=run, number=100)
print(t)