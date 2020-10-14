from phantom.phantom import phantom_fractions, phantom_tissues, plot_phantom
import matplotlib.pyplot as plt

#phantom = phantom_tissues()

phantom = phantom_fractions()
fig_t1, ax_t1 = plt.subplots(figsize=(12, 9))
tmp = ax_t1.imshow(phantom[0])
plt.title('Phantom: T1 values')
plt.colorbar(tmp)
plt.show()

# fig_t2, ax_t2 = plt.subplots(figsize=(12, 9))
# tmp = ax_t1.imshow(phantom[1])
# plt.title('Phantom: T2 values')
# plt.colorbar(tmp)
# plt.show()