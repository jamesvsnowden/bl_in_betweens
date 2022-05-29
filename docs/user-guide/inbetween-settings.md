
Settings for in-betweens are all available within the Shape Keys panel.

<!-- image of hero settings sub-panel -->

Each hero shape key will have an list of its in-between shape keys and their settings.

<!-- image of in-between settings sub-panel -->

Each in-between shape key will show its settings as well as which hero shape key it belongs to.

## Activation Value

The activation value is the value of the hero shape key at which the in-between shape key is fully activated. When you add a new in-between shape key the activation value is set to the current value of the hero shape key, but you can adjust it at any time. 

!!! note
    The activation value always lies within the minimum and maximum [activation range](#activation-range) including a little padding (0.1). You will not be able to adjust it beyond those limits.

The activation value is reflected in the [activation curve](#activation-curve) graph as the highest point on the curve. As you change the activation value the curve updates accordingly. This allows you to visualize the activation of the in-between

<!-- gif of activation value affecting curve -->

### Snap to Activation Value

<!-- image of highlighted snap to activation value button -->

The button next to the activation value allows you to snap the hero shape key's value to the in-between shape key's activation value in order to preview the in-between when fully activated.

!!! note
    If the hero shape key's value is being driven, the hero shape key's value will not change when using the **Snap to Activation Value** action.

## Activation Range

The activation range is the lower and upper values of the hero shape key within which the in-between shape key will be activated.

!!! note
    The [activation value](#activation-value) always lies within the minimum and maximum activation range values and you will not be able to set the minimum higher than the activation value - 0.1, nor the maximum lower than the activation value + 0.1.

The activation range is reflected in the [activation curve](#activation-curve) graph. As you change the activation range the curve updates accordingly.

<!-- gif of activation range affecting curve -->

## Activation Curve

The activation curve controls the interpolation of the in-between shape key with the hero shape key.

### Presets

<!-- grid of images for each combination of ramp, interpolation and easing -->

### Custom Curve



## Target Value

The target value is the value you want the in-between shape key to have when it is fully activated.