class Agent:
    def __init__(self, programme):
        self.programme = programme
        self.prediction_object = None

    def load_model(self, model_path):
        # Load the model from the specified path
        self.programme.load(model_path)

    def save_model(self, model_path):
        # Save the current model to the specified path
        self.programme.save(model_path)

    def reason(self):
        # Return the reason for the prediction
        return self.prediction_object.reasoning

    def reset(self):
        # Reset the internal state
        self.prediction_object = None


__all__ = ["Agent"]
