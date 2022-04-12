# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from ax.benchmark2.benchmark_method import BenchmarkMethod
from ax.modelbridge.generation_strategy import GenerationStep, GenerationStrategy
from ax.modelbridge.registry import Models
from ax.models.torch.botorch_modular.surrogate import Surrogate
from ax.service.scheduler import SchedulerOptions
from ax.utils.common.constants import Keys
from botorch.acquisition.monte_carlo import qNoisyExpectedImprovement
from botorch.models.gp_regression import FixedNoiseGP


def get_sobol_gpei() -> BenchmarkMethod:
    model_gen_kwargs = {
        "model_gen_options": {
            Keys.OPTIMIZER_KWARGS: {
                "num_restarts": 50,
                "raw_samples": 1024,
            },
            Keys.ACQF_KWARGS: {
                "prune_baseline": True,
                "qmc": True,
                "mc_samples": 512,
            },
        }
    }

    generation_strategy = GenerationStrategy(
        name="Modular::Sobol+GPEI",
        steps=[
            GenerationStep(model=Models.SOBOL, num_trials=5, min_trials_observed=3),
            GenerationStep(
                model=Models.BOTORCH_MODULAR,
                num_trials=-1,
                model_kwargs={
                    "surrogate": Surrogate(FixedNoiseGP),
                    "botorch_acqf_class": qNoisyExpectedImprovement,
                },
                model_gen_kwargs=model_gen_kwargs,
            ),
        ],
    )

    scheduler_options = SchedulerOptions(total_trials=30)

    return BenchmarkMethod(
        name="Modular::Sobol+GPEI",
        generation_strategy=generation_strategy,
        scheduler_options=scheduler_options,
    )
